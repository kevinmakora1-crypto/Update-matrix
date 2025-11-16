import frappe
from one_fm.custom.workflow.workflow import get_workflow_json_file, create_workflow, delete_workflow
from one_fm.custom.assignment_rule.assignment_rule import get_assignment_rule_json_file, create_assignment_rule

def execute():
    delete_workflow(get_workflow_json_file("paci.json"))
    create_workflow(get_workflow_json_file("paci.json"))
    create_assignment_rule(get_assignment_rule_json_file("action_paci.json"))
    create_paci_process_task()

def create_paci_process_task():
    
    task = frappe.get_doc({
        "doctype": "Process Task",
        "naming_series": "P-TASK-.YYYY.-",
        "task": "Action PACI - get Civil ID done and delivered",
        "process_name": "Residency",
        "erp_document": "PACI",
        "task_type": "Repetitive",
        "is_erp_task": 1,
        "is_active": 1,
        "is_automated": 0,
        "is_routine_task": 0,
        "coordination_needed": "No",
        "hours_per_frequency": 0,
        "repeat_on_day": 0,
        "repeat_on_last_day": 0
    })
    task.insert(ignore_permissions=True)