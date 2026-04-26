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
			api_secret = generate_keys(user.name)
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