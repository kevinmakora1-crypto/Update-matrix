import frappe

def execute():
    workflow_states = {
        "Set Pick-up as Accommodation (Supervisor)": "Warning",
        "Pending GR Operator": "Warning",
        "Pending PRO": "Warning",
        "Pending Transportation Supervisor": "Warning",
        "Pending Supervisor": "Warning",
        "Reschedule Requested": "Danger"
    }
    
    for state_name, style in workflow_states.items():
        if frappe.db.exists("Workflow State", state_name):
            frappe.db.set_value("Workflow State", state_name, "style", style)
            print(f"Updated workflow state: {state_name} with style: {style}")
        else:
            print(f"Workflow state not found: {state_name}")
    
    frappe.db.commit()