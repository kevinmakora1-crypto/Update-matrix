import frappe
from one_fm.custom.assignment_rule.assignment_rule import get_assignment_rule_json_file, create_assignment_rule


def execute():
    process_task_name = frappe.db.get_value("Process Task", {"process_name": "Loan Management"}, "name")
    assignment_rule_data = get_assignment_rule_json_file("review_and_approve_loan_application_senior_accountant.json")
    if process_task_name:
        assignment_rule_data["custom_routine_task"] = process_task_name
    create_assignment_rule(assignment_rule_data)