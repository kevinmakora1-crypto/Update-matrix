import frappe
from one_fm.custom.assignment_rule.assignment_rule import get_assignment_rule_json_file, create_assignment_rule

def execute():
    create_assignment_rule(get_assignment_rule_json_file("submit_client_interview_shortlist_operations_supervisor.json"))
