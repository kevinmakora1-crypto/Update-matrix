import json
import frappe
from frappe import _
from frappe.utils import get_fullname
from bs4 import BeautifulSoup
from datetime import datetime,timezone
from one_fm.processor import is_user_id_company_prefred_email_in_employee
from one_fm.utils import get_gmail_service
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from frappe import _

def validate_todo(doc, method):
	notify_todo_status_change(doc)
	set_todo_type_from_refernce_doc(doc)

def notify_todo_status_change(doc):
	if doc.is_new():
		return
	status_in_db = frappe.db.get_value(doc.doctype, doc.name, 'status')
	if status_in_db != doc.status and doc.assigned_by != doc.allocated_to:
		user = frappe.session.user
		subject = _("{0}({1}) assignment is {2}".format(doc.reference_type, doc.reference_name, doc.status))
		email_content = _("""
                    	The assignment referenced to {0}({1}) is {2} by {3}. See Details Below <br> 
					<p>Description: {4} </p> <br>
					<p>Date of Allocation:{5}</p> <br>
					<p>Due Date:{6}</p> <br>
                     """.format(doc.reference_type, doc.reference_name, doc.status,\
                         	get_fullname(user),doc.description,doc.creation,doc.date))
		if doc.reference_type == "Task":
			task_subject = frappe.db.get_value("Task",doc.reference_name,"subject")
			subject = _("{0} '{1}'({2}) assignment is {3}".format(doc.reference_type, task_subject,doc.reference_name, doc.status))
			email_content+= f'<p>Subject:{task_subject}</p>'
		notification_log = frappe.new_doc('Notification Log')
		notification_log.subject = subject
		notification_log.email_content = email_content
		notification_log.for_user = doc.assigned_by
		notification_log.document_type = doc.doctype
		notification_log.document_name = doc.name
		notification_log.from_user = user
		# If notification log type is Alert then it will not send email for the log
		if send_notification_alert_only(doc.assigned_by):
			notification_log.type = 'Alert'
		else:
			notification_log.type = 'Assignment'
		notification_log.insert(ignore_permissions=True)

def send_notification_alert_only(user):
	if user == 'Administrator':
		return True
	if not is_user_id_company_prefred_email_in_employee(user):
		return True
	return False

def set_todo_type_from_refernce_doc(doc):
	if doc.reference_type and doc.reference_name:
		if doc.reference_type in ['Project', 'Task'] and frappe.get_meta(doc.reference_type).has_field('type'):
			doc.type = frappe.db.get_value(doc.reference_type, doc.reference_name, 'type')
		else:
			doc.type = "Action"


# Define the scope for Google Tasks API
SCOPES = ['https://www.googleapis.com/auth/tasks']

def authenticate_google_tasks(user_email):
    """Authenticate and return the Google Tasks service for a specific user."""
    creds = None
    token_path = frappe.get_site_path('private', 'files', f'{user_email}_token.json')

    try:
        # Check if credentials exist for the user
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    except:
        # If no valid credentials, request authorization for the user
        flow = InstalledAppFlow.from_client_secrets_file('/Users/samdani/Desktop/sample/sites/onefm.localhost/private/files/credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())

    return build('tasks', 'v1', credentials=creds)


def create_google_task_on_todo_creation(doc, method):
	employee_email = doc.allocated_to
	if not employee_email:
		frappe.throw(_("No assigned user found for this ToDo"))
	
	service = authenticate_google_tasks(employee_email)
	html_content = doc.description
	soup = BeautifulSoup(html_content, 'html.parser')
	task_notes = soup.find('p').get_text()
	task_title = doc.custom_google_task_title
	date_obj = datetime.strptime(doc.date, "%Y-%m-%d")
	due_date = date_obj.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc).isoformat()

	task_body = {
        'title': task_title,
        'notes': task_notes,
        'due': due_date
    }
	result = service.tasks().insert(tasklist='@default', body=task_body).execute()
	task_id = result['id']
	doc.custom_google_task_id = task_id 
	doc.save()
	print(f"Task created: {result['title']} (ID: {result['id']})")
	return result

def update_google_task_on_todo_status_change(doc, method):
	if doc.custom_google_task_id:
		employee_email = doc.allocated_to
		if not employee_email:
			frappe.throw(_("No assigned user found for this ToDo"))
		if doc.status == "Open":
			pass
		else:
			service = authenticate_google_tasks(employee_email)
			task = service.tasks().get(task=doc.custom_google_task_id).execute()
			task['status'] = 'completed'
			print("samdaniiii ia ma ")
			result = service.tasks().update(task=doc.custom_google_task_id, body=task).execute()
			print(f"Task '{result['title']}' marked as completed.")
			return result