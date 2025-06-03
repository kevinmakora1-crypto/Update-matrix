import frappe, requests, re
from frappe import _
from frappe.utils import getdate
from json import dumps
from httplib2 import Http
from frappe.desk.form.assign_to import get as get_assignments,add as add_assignment

from one_fm.processor import sendemail
from one_fm.api.doc_events import get_employee_user_id

def send_google_chat_notification(doc, method):
    """Hangouts Chat incoming webhook to send the Issues Created, in Card Format."""

    # Fetch the Key and Token for the API
    default_api_integration = frappe.get_doc("Default API Integration")

    google_chat = frappe.get_doc("API Integration",
        [i for i in default_api_integration.integration_setting
            if i.app_name=='Google Chat'][0].app_name)

    if google_chat.active:
        # Construct the request URL
        url = f"""{google_chat.url}/spaces/{google_chat.api_parameter[0].get_password('value')}/messages?key={google_chat.get_password('api_key')}&token={google_chat.get_password('api_token')}"""

        # Construct Message Body
        message = f"""<b>A new Issue has been created</b><br>
            <i>Details:</i> <br>
            Subject: {doc.subject} <br>
            Name: {doc.name} <br>
            Raised By (Email): {doc.raised_by} <br>
            Body: {doc.description}<br>
            """

        # Construct Card the allows Button action
        bot_message = {
            "cards_v2": [
                {
                "card_id": "IssueCard",
                "card": {
                "sections": [
                {
                    "widgets": [
                        {
                        "textParagraph": {
                        "text": message
                        }
                        },
                    {
                    "buttonList": {
                        "buttons": [
                        {
                            "text": "Open Document",
                            "onClick": {
                            "openLink": {
                                "url": frappe.utils.get_url(doc.get_url()),
                            }
                            }
                        },
                        ]
                    }
                    }
                ]
                }
                ]
            }
            }
            ]
        }

        # Call the API
        message_headers = {'Content-Type': 'application/json; charset=UTF-8'}
        http_obj = Http()
        response = http_obj.request(
            uri=url,
            method='POST',
            headers=message_headers,
            body=dumps(bot_message),
        )


def validate_hd_ticket(doc, event):
    bug_buster = frappe.get_all("Bug Buster",{'docstatus':1,'from_date':['<=',getdate()],'to_date':['>=',getdate()]},['employee'])
    if bug_buster:
        emp_user = frappe.get_value("Employee",bug_buster[0].employee,'user_id')
        if emp_user:
            doc.custom_bug_buster = emp_user

    if (doc.status == "Closed" or doc.status == "Resolved") and not doc.resolution_details:
        frappe.throw(_("Please fill in Resolution Details before closing the ticket."))


def notify_ticket_raiser_of_resolution_details(doc, event):
    if doc.status == "Closed":
        previous_doc = doc.get_doc_before_save() # Check if status was just changed to Closed
        if previous_doc and previous_doc.status != "Closed":
            try:
                subject = f"HD Ticket {doc.name} Closed"
                employee=  frappe.db.get_value("Employee", {"user_id": doc.raised_by}, ["employee_name"], as_dict=1)

                args = frappe._dict({
                    "employee_name": employee.employee_name,
                    "ticket_subject": doc.subject,
                    "resolution_details": doc.resolution_details,
                    "base_url": frappe.utils.get_url(),
                    "doc_type": doc.doctype,
                    "doc_name": doc.name
                })
                message = frappe.render_template('one_fm/templates/emails/notify_ticket_raiser_of_resolution.html', context=args)
                frappe.enqueue(method=sendemail, queue="short", recipients=doc.raised_by, subject=subject, content=message, is_external_mail=True, is_scheduler_email=True)
            except Exception as e:
                frappe.log_error(message=frappe.get_traceback(), title="HD Ticket")


def notify_ticket_raiser_of_receipt(doc, event):
    try:
        subject = f"HD Ticket {doc.name} Raised"
        employee=  frappe.db.get_value("Employee", {"user_id": doc.raised_by}, ["employee_name"], as_dict=1)

        args = frappe._dict({
            "employee_name": employee.employee_name,
            "ticket_subject": doc.subject,
            "base_url": frappe.utils.get_url(),
            "doc_type": doc.doctype,
            "doc_name": doc.name
        })
        message = frappe.render_template('one_fm/templates/emails/notify_ticket_raiser_receipt.html', context=args)
        frappe.enqueue(method=sendemail, queue="short", recipients=doc.raised_by, subject=subject, content=message, is_external_mail=True, is_scheduler_email=True)
    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="HD Ticket")
    
    
def notify_issue_raiser_about_priority(doc, event):
    if doc.ticket_type == "Bug":
        previous_doc = doc.get_doc_before_save()
        if previous_doc:
            if any((previous_doc.priority != doc.priority, previous_doc.ticket_type != doc.ticket_type)):
                status = "HotFix" if doc.priority == "Urgent" else "BugFix"
                is_hotfix = status == "HotFix"
                title = f"Ticket {doc.name} - {status}"
                content_prefix = "A HotFix is in the works and should be completed within 24 hrs." if is_hotfix else "A BugFix is in the works and should be completed within a few days."
                context = dict(
                    header="We understand the urgency, we are on it!" if is_hotfix else "It’s a bug and we’ll fix it!",
                    document_name=doc.name,
                    document_type=doc.doctype,
                    document_link=frappe.utils.get_url(doc.get_url()),
                    content_prefix=content_prefix,
                    title=title,
                    priority=doc.priority
                )
                msg = frappe.render_template('one_fm/templates/emails/notify_ticket_raiser_about_priority.html', context=context)
                frappe.enqueue(method=sendemail, queue="short", recipients=doc.raised_by, subject=title, content=msg, is_external_mail=True, is_scheduler_email=True)


def apply_ticket_escalation(doc, event):
    if doc.agreement_status != 'Failed':
        return

    additional_settings = frappe.get_single("HD Additional Settings")
    escalation_priorities = [record.priority for record in additional_settings.escalation_priorities]
    escalation_ticket_types = [record.ticket_type for record in additional_settings.escalation_ticket_types]

    if doc.priority not in escalation_priorities and doc.ticket_type not in escalation_ticket_types:
        return

    # Fetch bug buster and his reports to details
    bug_buster = frappe.db.exists("Employee", {'user_id': doc.custom_bug_buster})
    if not bug_buster:
        return

    bug_buster_reports_to_user_id = get_employee_user_id(frappe.db.get_value('Employee', bug_buster, 'reports_to'))

    # Fetch doc current assignments
    doc_assignments = [assignment.owner for assignment in get_assignments({'doctype': doc.doctype, 'name': doc.name})]

    # If reports to is not assigned then add assignment
    if bug_buster_reports_to_user_id not in doc_assignments:
        add_assignment({
            'assign_to': [bug_buster_reports_to_user_id],
            'doctype': doc.doctype,
            'name': doc.name,
            'description': _('HD Ticket {0} has been assigned to you due to escalation for failed SLA').format(doc.name),
        })


@frappe.whitelist()
def create_dev_ticket(name, description):
    """
    Create a Jira bug ticket from HD Ticket
    """
    import base64
    from frappe.utils import get_url_to_form
    try:
        doc = frappe.get_doc("HD Ticket", name)
        doc_link = frappe.utils.get_url(get_url_to_form(doc.doctype, doc.name))

        # Use fallback if description is not provided
        description = cleanhtml(description) or doc.subject

        email = frappe.conf.get("jira_email")
        api_token = frappe.conf.get("jira_api_token")
        jira_url = frappe.conf.get("jira_url") or "https://one-fm.atlassian.net"
        project = frappe.conf.get("project_id")

        if not all([email, api_token, project]):
            frappe.throw("Jira credentials not found in site_config.json")

        # Prepare authentication
        auth = base64.b64encode(f"{email}:{api_token}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        }

        data = {
                    "fields": {
                        "project": {"key": project},
                        "summary": doc.subject,
                        "description": {
                            "type": "doc",
                            "version": 1,
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": f"Link: {doc_link}"},
                                    ]
                                },
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": f"Status: {doc.status}"},
                                    ]
                                },
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": f"Priority: {doc.priority}"},
                                    ]
                                },
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": f"Ticket Type: {doc.ticket_type}"},
                                    ]
                                },
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": cleanhtml(description)},
                                    ]
                                },
                            ]
                        },
                        "issuetype": {"name": "Bug"}
                    }
                }


        url = f"{jira_url}/rest/api/3/issue"
        response = requests.post(url, headers=headers, json=data, timeout=5)

        if response.status_code == 201:
            issue_key = response.json().get("key")
            issue_url = f"{jira_url}/browse/{issue_key}"
            doc.db_set('custom_dev_ticket', issue_url)
            return {'status': 'success', 'jira_issue': issue_key}
        else:
            error_msg = response.json().get("errors") or response.text
            return {'error': 'Dev Ticket Error', 'message': f"Dev ticket could not be created:\n{error_msg}"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Dev Ticket Creation Error")
        return {'error': 'Dev Ticket Error', 'message': f"Dev ticket could not be created:\n {str(e)}"}


CLEANER = re.compile('<.*?>') 

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANER, '', raw_html)
  return cleantext.replace("\t", "").replace("\n", "")
