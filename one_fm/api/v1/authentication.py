import frappe
import pyotp
from frappe.utils import getdate
from frappe.twofactor import get_otpsecret_for_, process_2fa_for_sms, confirm_otp_token, get_email_subject_for_2fa,get_email_body_for_2fa
from frappe.integrations.oauth2 import get_token
from frappe.core.doctype.user.user import generate_keys
from frappe.utils.background_jobs import enqueue
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from frappe.frappeclient import FrappeClient
from frappe.utils import now_datetime
from six import iteritems
from frappe import _
import requests, json
from frappe.utils.password import update_password as _update_password
from twilio.rest import Client as TwilioClient
from one_fm.api.v1.utils import response, get_current_user_details
from one_fm.processor import sendemail, send_whatsapp



@frappe.whitelist(allow_guest=True)
def user_login(employee_id, password):
	try:
		username =  frappe.db.get_value("Employee", {'employee_id': employee_id}, 'user_id')
		if not username:
			return response("Bad Request", 400, None,  "No account found for Employee ID {employee_id}. Please check and try again.".format(employee_id=employee_id))
		
		auth = frappe.auth.LoginManager()
		auth.authenticate(user=username, pwd=password)
		auth.post_login()
		
		# Restoring exact structure from previous working commits
		msg = {'status': 200, 'text': "Success", 'user': frappe.session.user}
		user = frappe.get_doc('User', frappe.session.user)
		
		# Generate or retrieve API keys
		if user.api_key and user.api_secret:
			api_secret = user.get_password('api_secret')
			msg['token'] = f"token {user.api_key}:{api_secret}"
		else:
			session_user = frappe.session.user
			frappe.set_user('Administrator')
			try:
				api_secret = generate_keys(user.name)
			finally:
				frappe.set_user(session_user)
			user.reload()
			msg['token'] = f"token {user.api_key}:{api_secret}"
		
		# Fetch details for the logged in user
		u_user, u_roles, u_employee = get_current_user_details()
		
		msg.update(u_employee)
		msg.update({"roles": u_roles})
		
		if any(role in u_roles for role in ["Operations Manager", "Projects Manager", "Site Supervisor"]):
			msg.update({"supervisor": 1})
		else:
			msg.update({"supervisor": 0})
			
		endpoint_state = frappe.db.get_single_value("ONEFM General Setting", 'enable_face_recognition_endpoint')
		msg['endpoint_state'] = endpoint_state
		msg['employee_endpoint_state'] = u_employee.get('custom_enable_face_recognition')
		msg['shift_working'] = u_employee.get('shift_working')
		
		return response("success", 200, msg)

	except frappe.exceptions.AuthenticationError:
		return response("error", 401, None, "Incorrect password. Please try again.")
	except Exception as e:
		frappe.log_error(title="API Login Reverted Crash", message=frappe.get_traceback())
		return response("error", 500, None, str(e))

@frappe.whitelist(allow_guest=True)
def enrollment_status(employee_id: str):
	try:
		if not employee_id:
			return response("error", 404, "Employee ID is required")
		employee = frappe.db.get_value(
			'Employee', 
			{'employee_id':employee_id} 
			,['status', 'enrolled', 'registered', 'employee_name', 'user_id','employee_name_in_arabic'], as_dict=1)
		if employee:
			if (employee.status in ['Left', 'Court Case']):
				return response("error", 404, {}, f"Employee is not active")
			elif (not employee.user_id):
				return response("error", 404, {}, f"No active user account or login email found for {employee_id}".format(employee_id=employee_id))
			else:
				return response("success", 200, {
					"enrolled": employee.enrolled,
					"registered": employee.registered, 
					"employee_name":employee.employee_name,
					"employee_name_ar":employee.employee_name_in_arabic},
				)
		else:
			return response("error", 404, {}, f"Employee ID {employee_id} does not exist")
	except Exception as e:
		return response("error", 500, {}, str(e))

@frappe.whitelist()
def fetch_employee_checkin_list(from_date=None, to_date=None, limit=20, page_number=1):
	""""
	returns an array of check in objects which belongs to the logged in employee

	Params
	from_date - begining date
	to_date - ending date
	limit - paginated by how many objects
	page_number - page to jump to


	returns
	no_of_pages - Total number of pages based on the limit
	current_page
	data - array of paginated check in objects
	number_of_check_in - total number of check in objects
	
	"""
	try:
		user_id = frappe.session.user
		if user_id is None:
			return response("Invalid authentication credentials", 400, None, "Invalid authentication credentials")
		employee = frappe.get_doc("Employee", {"user_id": user_id})
		if employee is None:
			return response("No account found for Employee ID", 400)
		if not isinstance(page_number, int):
			return response("Invalid page number", 400, None, "Page number must be an integer value.")
		if not isinstance(limit, int):
			return response("Invalid page limit", 400, None, "Page limit must be an integer value.")
		if from_date is not None and to_date is None:
			to_date = from_date 
		if from_date is not None:
			try:
				from_date = getdate(from_date)
			except:
				from_date = None
		if to_date is not None:
			try:
				to_date = getdate(to_date)
			except:
				to_date = None
		if from_date and to_date:
			if from_date > to_date:
				return response("Bad request", 400, None, "From date cannot be greater than To date")
		check_list = frappe.db.get_list("Employee Checkin", filters={"employee": employee.name, "time": ["between", (from_date, to_date)]}, fields=["name", "time", "log_type"])
		if len(check_list) < 1:
			return response("No check-ins found in the selected date range", 200)
		no_of_pages = len(check_list) // limit if len(check_list) % limit == 0 and len(check_list) // limit > 0 else (len(check_list) // limit) + 1
		if page_number > no_of_pages or page_number < 1:
			return response("Page not found", 404, None, f"Enter a page number within 1 - {no_of_pages}")
		end = page_number * limit
		check_in = check_list[(end - limit): end]
		data = {
			"no_of_pages": no_of_pages,
			"current_page": page_number,
			"data": check_in,
			"number of checkin": len(check_list)
		}
		return response("Success", 200, data)
	except Exception as e:
		frappe.log_error(title="API Authentication", message=frappe.get_traceback())
		response("Internal Server Error", 500, None, str(e))

@frappe.whitelist(allow_guest=True)
def new_forgot_password(employee_id=None):
	"""
	validates the employee_id and returns the employee_user_id, which will be used to generate OTP

	Params
	employee_id

	returns
	employee_user_id
	
	"""
	if not employee_id:
		return response("Bad Request", 400, None, "Employee ID is required. Please enter your Employee ID.")

	employee_user_id =  frappe.get_value("Employee", {'employee_id': employee_id}, 'user_id')
	
	if not employee_user_id:
		return response("Bad Request", 404, None, "No account found for Employee ID {employee_id}. Please check and try again.".format(employee_id=employee_id))

	return response("success", 200, {"employee_user_id": employee_user_id})

@frappe.whitelist(allow_guest=True)
def get_otp(employee_user_id: str=None, otp_source: str=None):
	"""
	sends OTP to the employee 

	params
	employee_user_id
	otp_source - where you want the OTP to be sent to sms, whatsapp, mail

	returns
	success message
	temp_id - which would be used to verify the authenticity of the OTP
	"""
	otp_secret = get_otpsecret_for_(employee_user_id)
	token = int(pyotp.TOTP(otp_secret).now())
	tmp_id = frappe.generate_hash(length=8)
	frappe.cache().set_value(f"otp_reset_{tmp_id}", employee_user_id, expires_in_sec=600)

	if otp_source.lower() == "sms":
		verification_obj = process_2fa_for_sms(employee_user_id, token, otp_secret)
	else:
		return response("Bad Request", 400, None, f"Unsupported OTP source: {otp_source}. Only SMS is supported.")

	result = {
		"message": "Password reset instructions sent via {otp_source}".format(otp_source=otp_source),
		"temp_id": tmp_id,
	}

	return response("Success", 201, result)
@frappe.whitelist(allow_guest=True)
def set_password(employee_user_id, new_password, tmp_id=None, otp=None):
	"""
	used to set the new password

	params
	new_password
	employee_user_id
	tmp_id
	otp

	returns
	success message
	
	"""
	try:
		if not tmp_id or frappe.cache().get_value(f"otp_reset_{tmp_id}") != employee_user_id:
			return response("error", 401, None, "Invalid or expired OTP session token.")

		if not otp:
			return response("error", 400, None, "OTP is required.")

		import pyotp
		otp_secret = get_otpsecret_for_(employee_user_id)
		if not pyotp.TOTP(otp_secret).verify(otp, valid_window=10):
			return response("error", 401, None, "Invalid or expired OTP.")

		frappe.cache().delete_value(f"otp_reset_{tmp_id}")

		_update_password(employee_user_id, new_password)
		frappe.db.set_value("Employee", {'user_id': employee_user_id}, "registered", 1)
		message =  {
				'message': _('Password Updated!')
			}
		return response("Success", 200, message)
	except Exception as e:
		return response("Error", 500, {}, str(e))