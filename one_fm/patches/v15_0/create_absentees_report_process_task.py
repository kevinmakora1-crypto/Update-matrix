import frappe

def execute():
    method = "one_fm.utils.check_consecutive_absences_task"
    document = "Attendance"
    
    if not frappe.db.exists("Method", method):
        frappe.get_doc({
            "method": method,
            "document_type": document,
            "description": "7 Days Absence Alert",
            "doctype": "Method"
        }).insert(ignore_permissions=True)

    process_name = "Attendance Process"
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

    if not frappe.db.exists("Process Task", process_name):
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
            "cron_format": "0 5 * * *", 
            "hours_per_frequency": 0.500,
            "coordination_needed": "No",
            "start_date": frappe.utils.today(),
            "doctype": "Process Task"
        }).insert(ignore_permissions=True)