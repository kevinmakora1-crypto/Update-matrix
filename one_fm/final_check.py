import frappe
from frappe.desk.form.assign_to import get

def run():
    name = "HR-ERE-2026-04-00009"
    doc = frappe.get_doc("Employee Resignation Extension", name)
    print(f"Document: {name}")
    print(f"Workflow State: {doc.workflow_state}")
    print(f"Operations Manager: {doc.operations_manager}")
    
    assignments = get({"doctype": doc.doctype, "name": doc.name})
    print(f"Current Assignments: {assignments}")
    
    if not assignments and doc.workflow_state == "Pending Operations Manager":
        print("Re-applying assignment rules...")
        from frappe.automation.doctype.assignment_rule.assignment_rule import apply
        apply(doc)
        frappe.db.commit()
        assignments = get({"doctype": doc.doctype, "name": doc.name})
        print(f"Assignments after re-apply: {assignments}")

