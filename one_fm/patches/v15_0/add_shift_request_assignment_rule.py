from one_fm.custom.assignment_rule.assignment_rule import get_assignment_rule_json_file, create_assignment_rule


def execute():
        create_assignment_rule(get_assignment_rule_json_file("shift_request_pending_approval_project_manager.json"))
        create_assignment_rule(get_assignment_rule_json_file("shift_request_pending_approval_reports_to.json"))