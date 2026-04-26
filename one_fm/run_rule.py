import frappe
def run():
    rule = frappe.get_doc("Assignment Rule", "Employee Resignation Extension - Pending Operations Manager")
    print(f"Condition: {rule.assign_condition}")
    print(f"Unassign: {rule.unassign_condition}")
    print(f"Assign To Field: {rule.get('field')}")
    print(f"Disabled: {rule.disabled}")
    print(f"Rule Type: {rule.rule}")
    print(f"DocType: {rule.document_type}")
