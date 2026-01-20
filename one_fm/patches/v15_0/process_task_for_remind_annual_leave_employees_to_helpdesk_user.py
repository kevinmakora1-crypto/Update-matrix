from frappe.utils import today
from one_fm.utils import create_process_task

def execute():
    create_process_task(
        "Leave Management",  # process_name
        "Leave Application",  # erp_document
        "Remind helpdesk user on leave application",  # task_description
        method="one_fm.overrides.leave_application.remind_annual_leave_employees_to_helpdesk_user",
        frequency="Cron",
        cron_format="00 8 * * *",
        process_owner=None,
        business_analyst=None,
        task_type="Routine",
        is_routine_task=1,
        is_automated=1
    )
