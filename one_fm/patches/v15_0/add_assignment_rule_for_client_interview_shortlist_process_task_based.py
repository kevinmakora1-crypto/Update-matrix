import frappe
from frappe.utils import today
from one_fm.setup.assignment_rule import create_assignment_rule, get_assignment_rule_json_file

def execute():
    process_task = create_process_task()
    assignment_rule_data = get_assignment_rule_json_file("review_approve_client_interview_shortlist_operations_manager.json")
    if process_task:
        process_name = process_task.name
        if process_task.employee:
            employee_data = frappe.db.get_value("Employee", process_task.employee, ["employee_name", "user_id", "department"], as_dict=True)
            if employee_data:
                assignment_rule_data["employee_name"] = employee_data.employee_name
                assignment_rule_data["employee_user"] = employee_data.user_id
                assignment_rule_data["department"] = employee_data.department
        create_assignment_rule(assignment_rule_data, process_name)

def create_process_task():
    process_name = "Client Interview"
    if not frappe.db.exists("Process", process_name):
        frappe.get_doc({
            "process_name": process_name,
            "description": process_name,
            "doctype": "Process",
            "process_owner": "Administrator",
            "process_owner_name": "Administrator",
            "business_analyst": "Administrator",
            "business_analyst_name": "Administrator"
        }).insert(ignore_permissions=True)

    task_type = "Repetitive"
    if not frappe.db.exists("Task Type", task_type):
        frappe.get_doc({
            "name": task_type,
            "is_routine_task": 0,
            "doctype": "Task Type"
        }).insert(ignore_permissions=True)

    process_task = frappe.get_doc({
        "naming_series": "P-TASK-.YYYY.-",
        "process_name": process_name,
        "is_erp_task": 1,
        "is_automated": 0,
        "is_active": 1,
        "erp_document": "Client Interview Shortlist",
        "task": "Review and Approve Client Interview Shortlist",
        "task_type": "Repetitive",
        "frequency": "",
        "repeat_on_day": 0,
        "repeat_on_last_day": 0,
        "hours_per_frequency": 0.0,
        "coordination_needed": "No",
        "employee": "HR-EMP-00001",
        "start_date": today(),
        "report_frequency": "",
        "doctype": "Process Task",
        "coordination_method": [],
        "repeat_on_days": []
    }).insert(ignore_permissions=True)
    return process_task
