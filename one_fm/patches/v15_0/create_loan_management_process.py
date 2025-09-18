import frappe

def execute():
    method = "one_fm.loan.action_loan_disbursement"
    document = "Loan"
    
    if not frappe.db.exists("Method", method):
        frappe.get_doc({
            "method": method,
            "document_type": document,
            "description": "Action Loan Disbursement",
            "doctype": "Method"
        }).insert(ignore_permissions=True)

    process_name = "Loan Management"
    if not frappe.db.exists("Process", process_name):
        frappe.get_doc({
            "process_name": process_name,
            "description": "Loan Management Process",
            "doctype": "Process",
            "process_owner_name": "Administrator",
            "process_owner": "Administrator"
        }).insert(ignore_permissions=True)

    task_type = "Repetitive"
    if not frappe.db.exists("Task Type", task_type):
        frappe.get_doc({
            "name": task_type,
            "is_routine_task": 0,
            "doctype": "Task Type"
        }).insert(ignore_permissions=True)

    existing_task = frappe.db.exists("Process Task", {
        "process_name": process_name,
        "task": "Action Loan Disbursement",
        "erp_document": document
    })
    
    if not existing_task:
        frappe.get_doc({
            "naming_series": "P-TASK-.YYYY.-",
            "process_name": process_name,
            "is_erp_task": 1,
            "is_automated": 0,
            "is_active": 1,
            "erp_document": document,
            "task": "Action Loan Disbursement",
            "task_type": task_type,
            "method": method,
            "frequency": "Daily",
            "hours_per_frequency": 0.5,
            "coordination_needed": "No",
            "start_date": frappe.utils.today(),
            "department": "Operations - ONEFM",
            "employee": "HR-EMP-00114",
            "repeat_on_day": 0,
            "repeat_on_days": [],
            "repeat_on_last_day": 0,
            "report_frequency": "",
            "doctype": "Process Task"
        }).insert(ignore_permissions=True)
        
        print(f"Created Process Task for {process_name}")
    else:
        print(f"Process Task for {process_name} already exists")