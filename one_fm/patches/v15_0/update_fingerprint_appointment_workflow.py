import frappe
from one_fm.custom.workflow.workflow import delete_workflow, get_workflow_json_file, create_workflow
from one_fm.setup.assignment_rule import create_assignment_rule, get_assignment_rule_json_file

def execute():
    try:
        create_transportation_supervisor_role()
        recreate_fingerprint_appointment_workflow()
        create_fingerprint_appointment_assignment_rules()
        frappe.db.commit()
        print("Patch executed successfully")
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error in patch execution: {str(e)}", "Fingerprint Appointment Patch")
        raise


def create_transportation_supervisor_role():
    if frappe.db.exists("Role", "Transportation Supervisor"):
        print("Transportation Supervisor role already exists")
        return
    
    role = frappe.get_doc({
        "doctype": "Role",
        "role_name": "Transportation Supervisor",
        "desk_access": 1,
        "disabled": 0,
        "two_factor_auth": 0,
        "is_custom": 0
    })
    role.insert(ignore_permissions=True)
    print("Transportation Supervisor role created")


def recreate_fingerprint_appointment_workflow():
    workflow_file = get_workflow_json_file("fingerprint_appointment.json")
    delete_workflow(workflow_file)
    create_workflow(workflow_file)
    print("Fingerprint Appointment workflow recreated")


def create_fingerprint_appointment_assignment_rules():
    assignment_rules = [
        "action_fingerprint_appointment_pro.json",
        "action_fingerprint_appointment_supervisor.json",
        "action_fingerprint_appointment_transportation_supervisor.json",
        "confirm_site_pickup_for_fingerprint_assignment.json"
    ]
    
    for rule_file in assignment_rules:
        create_assignment_rule(get_assignment_rule_json_file(rule_file))
        print(f"Assignment rule created: {rule_file}")