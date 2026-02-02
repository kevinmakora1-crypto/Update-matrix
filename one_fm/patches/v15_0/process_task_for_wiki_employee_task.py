import frappe
from frappe.utils import today
from one_fm.utils import create_process_task

def execute():
    create_process_task(
        "Others",  # process_name
        "User",  # erp_document
        "Unlink default workspace from new user after 30 days",  # task_description
        method="one_fm.overrides.user.unlink_wiki_workspace_from_user",
        frequency="Daily",
        cron_format="",  # Not needed for Daily
        process_owner=None,
        business_analyst=None,
        task_type="Routine",
        is_routine_task=1,
        is_automated=1
    )
    create_process_task(
        "Others",  # process_name
        "Employee",  # erp_document
        "Create wiki assessment todo for new employee after 30 days",  # task_description
        method="one_fm.overrides.employee.create_wiki_assessment_todo_for_employees",
        frequency="Daily",
        cron_format="",  # Not needed for Daily
        process_owner=None,
        business_analyst=None,
        task_type="Routine",
        is_routine_task=1,
        is_automated=1
    )
