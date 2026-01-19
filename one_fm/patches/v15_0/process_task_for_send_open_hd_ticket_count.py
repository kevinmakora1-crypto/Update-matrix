import frappe
from frappe.utils import today
from one_fm.utils import create_process_task

def execute():
    create_process_task(
        "HelpDesk Process",
        "HD Ticket",
        "Send Open HD Ticket Count",
        method="one_fm.events.issue.send_open_hd_ticket_count_to_google_chat_notification",
        frequency="Cron",
        cron_format="00 8 * * 0,1,2,3,4",
        process_owner=None,
        business_analyst=None,
        task_type="Routine",
        is_routine_task=1,
        is_automated=1
    )
