import frappe
from one_fm.setup.assignment_rule import create_assignment_rule, get_assignment_rule_json_file

def execute():
    create_assignment_rule(get_assignment_rule_json_file("assign_rfp_owner_on_rfp_return_to_draft.json"))
