import json
import frappe
from frappe import _
from frappe.utils import get_fullname, get_url_to_form, getdate
from bs4 import BeautifulSoup
from datetime import datetime,timezone, timedelta
from one_fm.processor import is_user_id_company_prefred_email_in_employee, sendemail
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

def get_google_task_service(employee_email):
    credentials_path = frappe.get_site_path('private', 'files', 'gcp.json')
    try:
        with open(credentials_path, 'r') as file:
            credentials_dict = json.load(file)
    except Exception:
        pass
    credentials = service_account.Credentials.from_service_account_info(credentials_dict, scopes=['https://www.googleapis.com/auth/tasks'])
    delegated_credentials = credentials.with_subject(employee_email)
    return build('tasks', 'v1', credentials=delegated_credentials)\
    
def create_google_task_on_todo_creation(doc, method):
    frappe.enqueue(create_google_task_on_todo_creation_in_erp(doc=doc, method=method),is_async=True)

def create_google_task_on_todo_creation_in_erp(doc, method):
    employee_email = doc.allocated_to
    if not employee_email:
        frappe.throw(_("No assigned user found for this ToDo"))
    service = get_google_task_service(employee_email)
    task_exists = check_google_task_exists(service, doc.custom_google_task_id)
    if task_exists:
        return
    task_notes = create_description_for_google_todo(doc)
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
    send_email_on_todo_created(doc)
    return result

def check_google_task_exists(service, task_id):
    try:
        # Get all task lists
        tasklists = service.tasklists().list().execute()
        for tasklist in tasklists.get('items', []):
            # Fetch tasks in the current task list
            tasks = service.tasks().list(tasklist=tasklist['id']).execute()
            # Check if the task_id exists in the tasks
            if any(task['id'] == task_id for task in tasks.get('items', [])):
                return True
    except Exception as e:
        frappe.throw(_("Error while checking tasks: {e}"))
    return False

def create_description_for_google_todo(doc):
    task_notes = ""
    try:
        task_notes = convert_html_to_plain_text( doc.description)
    except:
        task_notes = doc.description
    if doc.reference_type and doc.reference_name:
        todo_reference = get_url_to_form("Todo", doc.name) if doc.name else ""
        todo_doc_type = doc.reference_type if doc.reference_type else ""
        todo_reference_link = get_url_to_form(todo_doc_type, doc.reference_name) if doc.reference_name else ""
        task_notes +=f"""
		ToDo Reference: {todo_reference}
		Reference DocType: {todo_doc_type}
		Reference Name: {todo_reference_link}
		"""
    return task_notes

def convert_html_to_plain_text(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
        text_output = "\n".join(paragraphs)

        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            table_content = "\n".join(
                f"{' : '.join(td.get_text(strip=True) for td in row.find_all('td'))}" for row in rows
            )
            text_output += "\n\nDetails:\n" + table_content +"\n"

        return text_output
    except Exception as e:
        print(f"Error converting HTML to plain text: {e}")
        return "Failed to parse content."


def update_google_task_on_todo_status_change(doc, method):
    # Skip for newly created ToDos
    if doc.is_new():
        return
    
    if doc.custom_google_task_id:
        employee_email = doc.allocated_to
        if not employee_email:
            frappe.throw(_("No assigned user found for this ToDo"))
        service = get_google_task_service(employee_email)
        try:
            task = service.tasks().get(tasklist='@default', task=doc.custom_google_task_id).execute()
        except:
            task = create_google_task_on_todo_creation_in_erp(doc, method)
        task_title = doc.custom_google_task_title
        task_notes = create_description_for_google_todo(doc)
        date_obj = datetime.strptime(doc.date, "%Y-%m-%d")
        due_date = date_obj.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc).isoformat()
        task['title'] = task_title
        task['notes'] = task_notes
        task['due'] = due_date
        if doc.status == "Open":
            task['status'] = 'needsAction'
        else:
            task['status'] = 'completed'
        result = service.tasks().update(tasklist='@default',task=doc.custom_google_task_id, body=task).execute()
        return result
    
def get_mapped_status_from_google_task(task):
    """
        Map google task status to ERP ToDo status
    """
    if task.get('deleted'):
        return 'Cancelled'
    if task.get('status') == 'completed':
        return 'Closed'
    return 'Open'
    
@frappe.whitelist()
def sync_google_tasks_with_todos():
    try:
        active_users = frappe.get_all("User", {'enabled': 1})
        user_emails_having_google_account = [user.name for user in active_users if is_user_id_company_prefred_email_in_employee(user.name)]

        # Batching user emails in group of 5
        batch_size = 5
        for i in range(0, len(user_emails_having_google_account), batch_size):
            batch_user_emails = user_emails_having_google_account[i:i+batch_size]
            frappe.enqueue(sync_google_tasks_for_users, user_emails=batch_user_emails, is_async=True)

        return { 'error': False, 'message' : 'Google Tasks synchronized successfully' }
    
    except Exception as e:
        frappe.log_error(str(e), "Failed to sync google tasks to ERP ToDo")
        return { 'error': True, 'message' : str(e) }
    

def sync_google_tasks_for_users(user_emails=[]):
    all_google_tasks = []

      # Iterate through user emails having google account and fetch each user's tasks
    for user_email in user_emails:
        try:
            service = get_google_task_service(user_email)

            ten_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=10)
            updated_min = ten_minutes_ago.isoformat()

            results = service.tasks().list(tasklist='@default', showHidden=True, showDeleted=True, updatedMin=updated_min).execute()
            user_tasks = results.get('items', [])

            # Append user_email to each google_task for later use in allocated_to field
            for task in user_tasks:
                task['user_email'] = user_email

            all_google_tasks.extend(user_tasks)
        except Exception as e:
            frappe.log_error(str(e), f"Failed to fetch tasks for user {user_email}")

    # Iterate through all Google tasks and sync them to ERP ToDo
    for google_task in all_google_tasks:
        try:
            google_task_id = google_task['id']

            todo = frappe.get_all('ToDo', filters={'custom_google_task_id': google_task_id}, limit=1)

            due_date_str = google_task.get('due', None)
            due_date = getdate(due_date_str) if due_date_str else None
            task_title = google_task.get('title', '')[:100]
            task_description = google_task.get('notes', '') or google_task.get('title', '')
            allocated_to = google_task.get('user_email', '')
            mapped_status = get_mapped_status_from_google_task(google_task)
            custom_source = 'Google Task'

            if todo:
                todo = frappe.get_doc('ToDo', todo[0]['name'])
                todo.db_set("description", task_description)
                todo.db_set("status", mapped_status)
                todo.db_set("custom_google_task_title", task_title)
                todo.db_set("date", due_date)
                todo.db_set("allocated_to", allocated_to)
                todo.db_set("custom_source", custom_source)
            else:
                # If ToDo doesn't exist, create a new ToDo with google task details
                new_todo = frappe.get_doc({
                    'doctype': 'ToDo',
                    'description': task_description,
                    'date': due_date,
                    'status': mapped_status,
                    'custom_google_task_title': task_title,
                    'custom_google_task_id': google_task_id,
                    'allocated_to': allocated_to,
                    'custom_source':custom_source
                })
                new_todo.insert(ignore_permissions=True)

        except Exception as e:
            frappe.log_error(str(e), f"Failed to sync Google task {google_task_id} to ERP ToDo")


@frappe.whitelist()
def send_email_on_todo_created(doc):
    user_id = frappe.session.user
    user_email = frappe.db.get_value("User", user_id, "email")
    if user_email == doc.allocated_to:
        return
    sender = frappe.get_value("Email Account", filters = {"default_outgoing": 1}, fieldname = "email_id") or None
    recipients = [doc.allocated_to]
    task_id = doc.custom_google_task_id
    task_title = doc.custom_google_task_title
    task_notes = create_description_for_google_todo(doc)
    date_obj = datetime.strptime(doc.date, "%Y-%m-%d")
    due_date = date_obj.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc).isoformat()
    if doc.status == "Open":
        status = 'needsAction'
    else:
        status = 'completed'
    source = doc.custom_source
    message = f'''
		Google Task ID : {task_id}
		Title : {task_title}
		Description : {task_notes}
		Due Date : {due_date}
		Status : {status}
		Task has been Created via : {source}
	'''
    subject = f'''Task has been Created via  {source} '''
    sendemail(sender=sender, recipients= recipients,
            message=message, subject=subject, delayed=False, is_scheduler_email=False,is_external_mail=True)
