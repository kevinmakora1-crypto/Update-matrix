import frappe
from one_fm.custom.workflow.workflow import get_workflow_json_file, create_workflow
from one_fm.custom.assignment_rule.assignment_rule import get_assignment_rule_json_file, create_assignment_rule

def execute():
    create_workflow(get_workflow_json_file("attendance_amendment.json"))
    create_assignment_rule(get_assignment_rule_json_file("assign_to_site_supervisor.json"))
    create_assignment_rule(get_assignment_rule_json_file("assign_attendance_amendment_to_project_manager.json"))
