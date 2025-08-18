import frappe

def execute():
    method = "one_fm.one_fm.doctype.employee_daily_action.employee_daily_action.run_employee_daily_action_check_notifications"
    document = "Employee Daily Action"
    if not frappe.db.exists("Method", method):
        frappe.get_doc({
            "method": method,
            "document_type": document,
            "description": "Employee Daily Action Check Notifications",
            "doctype": "Method"
        }).insert(ignore_permissions=True)

    process_name = "Employee Daily Action Check"
    if not frappe.db.exists("Process", process_name):
        frappe.get_doc({
            "process_name": process_name,
            "description": process_name,
            "doctype": "Process",
            "process_owner_name": "Administrator",
            "process_owner": "Administrator"
        }).insert(ignore_permissions=True)

    task_type = "Routine"
    if not frappe.db.exists("Task Type", task_type):
        frappe.get_doc({
            "name": task_type,
            "is_routine_task": 1,
            "doctype": "Task Type"
        }).insert(ignore_permissions=True)

    frappe.get_doc({
        "naming_series": "P-TASK-.YYYY.-",
        "process_name": process_name,
        "is_erp_task": 1,
        "is_automated": 1,
        "is_active": 1,
        "erp_document": document,
        "task": process_name,
        "task_type": task_type,
        "method": method,
        "frequency": "Cron",
        "cron_format": "0 4 * * *",
        "hours_per_frequency": 0.1,
        "coordination_needed": "No",
        "start_date": "2025-08-18",
        "doctype": "Process Task"
    }).insert(ignore_permissions=True)