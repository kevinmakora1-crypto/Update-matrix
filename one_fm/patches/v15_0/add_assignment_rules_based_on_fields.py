import frappe
from one_fm.custom.assignment_rule.assignment_rule import create_assignment_rule, get_assignment_rule_json_file

def execute():
    rules = [
        "employee_resignation_pending_operations_manager.json",
        "employee_resignation_offboarding.json",
        "employee_resignation_withdrawal_pending_supervisor.json",
        "employee_resignation_withdrawal_operations_manager.json",
        "employee_resignation_withdrawal_offboarding.json",
        "erf_submit_recruitment_manager.json",
        "erf_under_review.json"
    ]
    
    for rule_file in rules:
        rule_data = get_assignment_rule_json_file(rule_file)
        if rule_data:
            create_assignment_rule(rule_data)
        else:
            frappe.log_error(title="Assignment Rule Install Error", message=f"Could not load {rule_file}")

