import frappe
from frappe.utils import today
from one_fm.setup.assignment_rule import create_assignment_rule, get_assignment_rule_json_file

def execute():
    process_task_name = create_process_task()
    assignment_rule_data = get_assignment_rule_json_file("assign_rfp_to_purchase_officer.json")
    create_assignment_rule(assignment_rule_data, process_task_name)


def create_process_task():
    process_name = "Requisition Process"
    if not frappe.db.exists("Process", process_name):
        frappe.get_doc({
            "process_name": process_name,
            "description": process_name,
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

    target_user_id = "h.razak@one-fm.com"

    employee = ""
    employee_name = ""
    employee_user_id = ""

    if frappe.db.exists("Employee", {"user_id": target_user_id}):
        employee, employee_name, employee_user_id = frappe.get_value("Employee", {"user_id": target_user_id}, ["name", "employee_name", "user_id"])

    process_task = frappe.get_doc({
        "naming_series": "P-TASK-.YYYY.-",
        "process_name": process_name,
        "is_erp_task": 1,
        "is_automated": 0,
        "is_active": 1,
        "erp_document": "Request for Purchase",
        "task": "Assign to Purchase Officer",
        "task_type": "Repetitive",
        "frequency": "",
        "repeat_on_day": 0,
        "repeat_on_last_day": 0,
        "hours_per_frequency": 0.0,
        "coordination_needed": "No",
        "employee": employee,
        "employee_name": employee_name,
        "employee_user": employee_user_id,
        "department": "Procurement and Warehouse  - ONEFM",
        "start_date": today(),
        "report_frequency": "",
        "doctype": "Process Task",
        "coordination_method": [],
        "repeat_on_days": []
    }).insert(ignore_permissions=True)
    return process_task.name