import json
import frappe
from frappe import _
from frappe.utils import get_fullname
from bs4 import BeautifulSoup
from datetime import datetime,timezone
from one_fm.processor import is_user_id_company_prefred_email_in_employee
from googleapiclient.discovery import build
from frappe import _
from google.oauth2 import service_account


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

def authenticate_google_tasks(employee_email):
	credentials_path = frappe.get_site_path('private', 'files', 'gcp.json')
	try:
		with open(credentials_path, 'r') as file:
			credentials_dict = json.load(file)
	except Exception:
		pass
	credentials = service_account.Credentials.from_service_account_info(credentials_dict, scopes=['https://www.googleapis.com/auth/tasks'])
	delegated_credentials = credentials.with_subject(employee_email)
	return build('tasks', 'v1', credentials=delegated_credentials)


def create_google_task_on_todo_creation(doc, method):
	employee_email = doc.allocated_to
	if not employee_email:
		frappe.throw(_("No assigned user found for this ToDo"))
	
	service = authenticate_google_tasks(employee_email)
	
	html_content = doc.description
	try:
		soup = BeautifulSoup(html_content, 'html.parser')
		task_notes = soup.find('p').get_text()
	except:
		task_notes = html_content
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
	return result

def update_google_task_on_todo_status_change(doc, method):
	if doc.custom_google_task_id:
		employee_email = doc.allocated_to
		if not employee_email:
			frappe.throw(_("No assigned user found for this ToDo"))
		service = authenticate_google_tasks(employee_email)
		task = service.tasks().get(tasklist='@default', task=doc.custom_google_task_id).execute()
		if doc.status == "Open":
			try:
				task_title = doc.custom_google_task_title
				html_content = doc.description
				try:
					soup = BeautifulSoup(html_content, 'html.parser')
					task_notes = soup.find('p').get_text()
				except:
					task_notes = doc.description
				date_obj = datetime.strptime(doc.date, "%Y-%m-%d")
				due_date = date_obj.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc).isoformat()
				task['title'] = task_title
				task['notes'] = task_notes
				task['due'] = due_date
				task['status'] = 'needsAction'
			except:
				pass
		else:
			task['status'] = 'completed'
		result = service.tasks().update(tasklist='@default',task=doc.custom_google_task_id, body=task).execute()
		return result