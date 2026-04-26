import frappe
from frappe.utils import cint

def run():
    # Update Workflow Transitions for Extension
    transitions = frappe.get_all("Workflow Transition", filters={"parent": "Employee Resignation Extension Workflow"}, fields=["name", "state", "action", "next_state"])
    for t in transitions:
        doc = frappe.get_doc("Workflow Transition", t.name)
        changed = False
        if doc.next_state == "Accepted by Supervisor":
            doc.next_state = "Pending Operations Manager"
            changed = True
        if doc.state == "Accepted by Supervisor":
            doc.state = "Pending Operations Manager"
            changed = True
        if changed:
            doc.save(ignore_permissions=True)
            print(f"Updated Transition: {doc.state} -> {doc.next_state}")
            
    # Need to make sure Workflow Document State exists!
    doc_states = frappe.get_all("Workflow Document State", filters={"parent": "Employee Resignation Extension Workflow"}, fields=["name", "state"])
    has_pending_om = False
    for s in doc_states:
        if s.state == "Pending Operations Manager":
            has_pending_om = True
        elif s.state == "Accepted by Supervisor":
            ws = frappe.get_doc("Workflow Document State", s.name)
            ws.state = "Pending Operations Manager"
            ws.avoid_settings = 0
            ws.doc_status = 0
            ws.allow_edit = "Operations Manager"
            ws.save(ignore_permissions=True)
            has_pending_om = True
            print("Renamed DocState Accepted by Supervisor -> Pending Operations Manager")
            
    if not has_pending_om:
        wf = frappe.get_doc("Workflow", "Employee Resignation Extension Workflow")
        wf.append("states", {
            "state": "Pending Operations Manager",
            "doc_status": 0,
            "allow_edit": "Operations Manager"
        })
        wf.save(ignore_permissions=True)
        print("Added Pending Operations Manager to States")
        
    # Revert the Assignment Rule back to what it was
    rule = frappe.get_doc("Assignment Rule", "Employee Resignation Extension - Pending Operations Manager")
    rule.assign_condition = 'doc.workflow_state == "Pending Operations Manager"'
    rule.unassign_condition = 'doc.workflow_state != "Pending Operations Manager"'
    rule.save(ignore_permissions=True)
    
    frappe.db.commit()
    print("Fixed Workflow to match Resignation cleanly.")
