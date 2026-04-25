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
			return response("Bad Request", 400, None,  "No account found for Employee ID {employee_id}.".format(employee_id=employee_id))
		
		# Authenticate
		auth = frappe.auth.LoginManager()
		auth.authenticate(user=username, pwd=password)
		auth.post_login()
		
		session_user = frappe.session.user
		if session_user == "Guest":
			session_user = username
			
		user = frappe.get_doc('User', session_user)
		
		# We've already fixed the keys, so this should be safe now
		api_secret = user.get_password('api_secret')
		
		msg = {
			'status': 200, 
			'text': "Success", 
			'user': session_user,
			'token': f"token {user.api_key}:{api_secret}"
		}
		
		# Fetch details for the logged in user
		# Temporary override session user to ensure get_current_user_details works
		orig_user = frappe.session.user
		frappe.set_user(session_user)
		try:
			u, u_roles, u_employee = get_current_user_details()
		finally:
			frappe.set_user(orig_user)
		
		if u_employee:
			msg.update(u_employee)
			msg['employee_endpoint_state'] = u_employee.get('custom_enable_face_recognition')
			msg['shift_working'] = u_employee.get('shift_working')
			
		msg.update({"roles": u_roles})
		
		if any(role in u_roles for role in ["Operations Manager", "Projects Manager", "Site Supervisor"]):
			msg.update({"supervisor": 1})
		else:
			msg.update({"supervisor": 0})
			
		endpoint_state = frappe.db.get_single_value("ONEFM General Setting", 'enable_face_recognition_endpoint')
		msg['endpoint_state'] = endpoint_state
		
		return response("success", 200, msg)

	except frappe.exceptions.AuthenticationError:
		return response("error", 401, None, "Incorrect password. Please try again.")
	except Exception as e:
		frappe.log_error(title="API Login Final Crash", message=frappe.get_traceback())
		return response("error", 500, None, f"Login failed: {str(e)}")

# ... (Include all other functions from the previous versions here) ...
@frappe.whitelist(allow_guest=True)
def login(client_id: str = None, grant_type: str = None, employee_id: str = None, password: str = None) -> dict:
	""" This method logs in the user provided appropriate paramaters. """
	if not client_id:
		return response("Bad Request", 400, None, "Client ID is missing. Please enter a valid Client ID.")
	
	if not grant_type:
		return response("Bad Request", 400, None, "Grant type is missing. Please specify the grant type.")
	
	if not employee_id:
		return response("Bad Request", 400, None, "Please enter your Employee ID.")
	
	if not password:
		return response("Bad Request", 400, None, "Please enter your password.")

	try:
		site = frappe.utils.cstr(frappe.local.conf.app_url)
		username =  frappe.db.get_value("Employee", {'employee_id': employee_id}, 'user_id')
		
		if not username:
			return response("Unauthorized", 401, None, "Employee ID not found. Please check and try again.")
		
		args = {
			'client_id': client_id,
			'grant_type': grant_type,
			'username': username,
			'password': password
		}
		headers = {'Accept': 'application/json'}
		session = requests.Session()
		auth_api = site + "api/method/frappe.integrations.oauth2.get_token"
		auth_api_response = session.post(
			auth_api,
			data=args, headers=headers
		)

		if auth_api_response.status_code == 200:
			frappe_client = FrappeClient(site[:-1], username=username, password=password)
			user, user_roles, user_employee =  frappe_client.get_api("one_fm.api.v1.utils.get_current_user_details")
			result = auth_api_response.json()
			result.update(user_employee)
			result.update({"roles": user_roles})
			if "Operations Manager" in user_roles or "Projects Manager" in user_roles or "Site Supervisor" in user_roles:
				result.update({"supervisor": 1})
			else:
				result.update({"supervisor": 0})

			return response("Success", 200, result)
		
		else:
			raw_error = json.loads(auth_api_response.content)
			if "message" in list(raw_error.keys()):
				return response("Bad Request", auth_api_response.status_code, None, raw_error['message'])
			
			return response("Bad Request", auth_api_response.status_code, None, json.loads(auth_api_response.content))

	except Exception as error:
		frappe.log_error(title="API Login", message=frappe.get_traceback())
		return response("Internal Server Error", 500, None, str(error))

@frappe.whitelist(allow_guest=True)
def forgot_password(employee_id: str = None, otp_source: str = None, is_new: int = 0) -> dict:
	if not employee_id:
		return response("Bad Request", 400, None, "Please enter your Employee ID.")

	if not otp_source:
		return response("Bad Request", 400, None, "Please select an OTP source (SMS, Email, or WhatsApp).")

	formatted_otp_source = otp_source.lower()

	try:
		employee_user_id =  frappe.get_value("Employee", {'employee_id': employee_id}, 'user_id')
		
		if not employee_user_id:
			return response("Bad Request", 404, None, "No account found for employee ID {employee_id}. Please check and try again.".format(employee_id=employee_id))
		
		if formatted_otp_source in ("sms", "whatsapp"):
			target_user = frappe.db.get_value('User', employee_user_id, ['phone', 'mobile_no'], as_dict=1)
			phone = target_user.mobile_no or target_user.phone

			if not phone:
				return response("Bad Request", 400, None, "No phone number found for user {user}.".format(user=employee_user_id))
		
		otp_secret = get_otpsecret_for_(employee_user_id)
		token = int(pyotp.TOTP(otp_secret).now())
		tmp_id = frappe.generate_hash(length=8)
		cache_2fa_data(employee_user_id, token, otp_secret, tmp_id)
		
		if formatted_otp_source == "sms":
			verification_obj = process_2fa_for_sms(employee_user_id, token, otp_secret)
		elif formatted_otp_source == "email":
			verification_obj = process_2fa_for_email(employee_user_id, token, otp_secret)
		elif formatted_otp_source == "whatsapp":
			verification_obj = process_2fa_for_whatsapp(employee_user_id, token, otp_secret)
		
		frappe.get_doc({
			"doctype":"Password Reset Token",
			"user":employee_user_id,
			"status": 'Inactive',
			"temp_id":tmp_id,
			"new_password": 1 if is_new else 0
		}).insert(ignore_permissions=True)

		result = {
			"message": "Password reset instructions sent via {otp_source}".format(otp_source=otp_source),
			"temp_id": tmp_id
		}

		return response("Success", 201, result)
	
	except Exception as error:
		frappe.log_error(title="API Forgot password", message=frappe.get_traceback())
		return response("Internal Server Error", 500, None, str(error))


@frappe.whitelist(allow_guest=True)
def verify_otp(otp, temp_id):
	try:
		login_manager = frappe.local.login_manager
		check_otp = confirm_otp_token(login_manager, otp, temp_id)
		password_token = frappe.db.get_value(
			"Password Reset Token",
			{"temp_id":temp_id}, 
			['name', 'status', 'expiration_time'],
			as_dict=1
		)
		if check_otp:
			frappe.db.set_value("Password Reset Token", {"temp_id":temp_id}, "status", "Active")
			return response ("success", 200, {
				"password_token":password_token.name,
				"message":"OTP verified successfully!"})
		frappe.db.set_value("Password Reset Token", {"temp_id":temp_id}, "status", "Revoked")
		return response("Error", 400, {}, "Incorrect OTP. Please check and enter the correct code.")
	except Exception as e:
		return response("Error", 500, {}, str(e) or "OTP verification failed!")


@frappe.whitelist(allow_guest=True)
def change_password(employee_id, new_password, password_token):
	try:
		employee_user = frappe.get_value("Employee", {'employee_id':employee_id}, ["user_id"])
		password_token_info = frappe.db.get_value(
			"Password Reset Token",
			{"name":password_token}, 
			['name', 'status', 'expiration_time', 'user', 'new_password'],
			as_dict=1
		)
		if (employee_user!=password_token_info.user):
			return response ("Error", 400, {}, "Password reset failed. The user details do not match.")
		elif password_token_info.status != "Active":
			return response ("Error", 400, {}, "Your password reset token has expired. Please request a new one.")

		_update_password(employee_user, new_password)
		frappe.db.set_value("Password Reset Token", password_token, "status", "Revoked")
		if password_token_info.new_password:
			frappe.db.set_value("Employee", {"employee_id":employee_id}, "registered", 1)
		return response ("Success", 200, {
			"message": "Password reset successful! Please login with your new password."
		}, "")
	except Exception as e:
		frappe.log_error(title="API Change password", message=frappe.get_traceback())
		return response ("Error", 500, {}, str(e))

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

def cache_2fa_data(user, token, otp_secret, tmp_id):
	expiry_time = 1800
	frappe.cache().set(tmp_id + '_token', token)
	frappe.cache().expire(tmp_id + '_token', expiry_time)
	for k, v in iteritems({'_usr': user, '_pwd': '12345', '_otp_secret': otp_secret}):
		frappe.cache().set("{0}{1}".format(tmp_id, k), v)
		frappe.cache().expire("{0}{1}".format(tmp_id, k), expiry_time)

def process_2fa_for_whatsapp(user, token, otp_secret):
	phone = frappe.db.get_value('User', user, ['phone', 'mobile_no'], as_dict=1)
	phone = phone.mobile_no or phone.phone
	status = send_token_via_whatsapp(otp_secret, token=token, phone_no=phone)
	return {
		'token_delivery': status,
		'prompt': status and 'Enter verification code sent to {}'.format(phone[:4] + '******' + phone[-3:]),
		'method': 'SMS',
		'setup': status
	}

def send_token_via_whatsapp(otpsecret, token=None, phone_no=None):
	hotp = pyotp.HOTP(otpsecret)
	content_variables= {'1': hotp.at(int(token))}
	send_whatsapp(sender_id=phone_no,template_name='authentication_code', content_variables=content_variables)
	return True

def process_2fa_for_email(user, token, otp_secret):
	otp_issuer = frappe.db.get_single_value('System Settings', 'otp_issuer_name')
	status = send_token_via_email(user, token, otp_secret, otp_issuer)
	return {
		'token_delivery': status,
		'prompt': status and _('Verification code has been sent to your registered email address.'),
		'method': 'Email',
		'setup': status
	}

def send_token_via_email(user, token, otp_secret, otp_issuer, subject=None, message=None):
	user_email = frappe.db.get_value('Employee', {"user_id":user}, 'personal_email')
	if not user_email: return False
	hotp = pyotp.HOTP(otp_secret)
	otp = hotp.at(int(token))
	template_args = {'otp': otp, 'otp_issuer': otp_issuer}
	if not subject: subject = get_email_subject_for_2fa(template_args)
	if not message: message = get_email_body_for_2fa(template_args)
	email_args = {'recipients': user_email, 'subject': subject, 'message': message, 'header': [_('Verfication Code'), 'blue'], 'delayed': False}
	enqueue(method=sendemail, queue='short', timeout=300, **email_args)
	return True