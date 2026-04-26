import frappe

def run():
    doc = frappe.get_doc("Employee Resignation Extension", "HR-ERE-2026-04-00009")
    print("Operations Manager:", doc.operations_manager)
    print("Workflow State:", doc.workflow_state)
