import frappe
from frappe.utils import today
from one_fm.utils import create_process_task

def execute():
    create_process_task(
        "Others",
        "Temporary Post",
        "Mark temporary posts as completed if the date ends",
        method="one_fm.operations.doctype.temporary_post.temporary_post.mark_temporary_posts_as_completed",
        frequency="Cron",
        cron_format="10 6 * * *",
        task_type="Routine",
        is_routine_task=1,
        is_automated=1
    )
