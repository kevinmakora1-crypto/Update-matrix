import frappe

def execute():
    rule_name = "Employee Resignation Withdrawal - Accepted by Supervisor"
    if not frappe.db.exists("Assignment Rule", rule_name):
        doc = frappe.new_doc("Assignment Rule")
        doc.name = rule_name
        doc.document_type = "Employee Resignation Withdrawal"
        doc.assign_condition = 'workflow_state == "Accepted by Supervisor"'
        doc.unassign_condition = 'workflow_state != "Accepted by Supervisor"'
        doc.rule = "Based on Field"
        doc.field = "operations_manager"
        doc.description = "Employee Resignation Withdrawal requires Operations Manager approval."
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            doc.append("assignment_days", {"day": day})
        doc.insert(ignore_permissions=True)
    
    frappe.db.commit()
