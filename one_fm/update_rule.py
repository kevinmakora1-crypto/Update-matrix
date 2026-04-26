 import frappe

def run():
    rules = frappe.get_all("Assignment Rule", filters={
        "document_type": ["in", ["Employee Resignation Extension", "Employee Resignation Withdrawal"]]
    })
    
    for r in rules:
        rule = frappe.get_doc("Assignment Rule", r.name)
        updated = False
        if rule.assign_condition and "doc." in rule.assign_condition:
            rule.assign_condition = rule.assign_condition.replace("doc.", "")
            updated = True
        if rule.unassign_condition and "doc." in rule.unassign_condition:
            rule.unassign_condition = rule.unassign_condition.replace("doc.", "")
            updated = True
            
        if updated:
            rule.save(ignore_permissions=True)
            print(f"Updated {rule.name}")

    frappe.db.commit()

