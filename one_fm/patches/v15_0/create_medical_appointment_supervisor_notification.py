import frappe

def execute():
    method = "one_fm.grd.doctype.medical_appointment.medical_appointment.send_supervisor_notification_on_pending_medical_appointments"
    document = "Medical Appointment"
    if not frappe.db.exists("Method", method):
        frappe.get_doc({
            "method": method,
            "document_type": document,
            "description": "Medical Appointment Supervisor Notifications",
            "doctype": "Method"
        }).insert(ignore_permissions=True)

    process_name = "Residency"
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
        "cron_format": "0 8 * * *",
        "hours_per_frequency": 0.5,
        "coordination_needed": "No",
        "start_date": frappe.utils.nowdate(),
        "doctype": "Process Task"
    }).insert(ignore_permissions=True)