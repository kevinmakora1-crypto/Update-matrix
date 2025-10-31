from one_fm.custom.workflow.workflow import delete_workflow, get_workflow_json_file, create_workflow
from one_fm.setup.assignment_rule import create_assignment_rule, get_assignment_rule_json_file

def execute():
    delete_workflow(get_workflow_json_file("fingerprint_appointment.json"))
    create_workflow(get_workflow_json_file("fingerprint_appointment.json"))

    create_assignment_rule(get_assignment_rule_json_file("action_fingerprint_appointment_pro.json"))
    create_assignment_rule(get_assignment_rule_json_file("action_fingerprint_appointment_supervisor.json"))
    create_assignment_rule(get_assignment_rule_json_file("action_fingerprint_appointment_transportation_supervisor.json"))
