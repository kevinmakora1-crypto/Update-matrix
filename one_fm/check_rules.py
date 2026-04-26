import frappe

def run():
    rules = frappe.get_all("Assignment Rule", filters={
        "document_type": ["in", ["Employee Resignation Extension", "Employee Resignation Withdrawal"]]
    }, fields=["name", "assign_condition", "unassign_condition", "rule", "field"])
    for r in rules:
        print(f"Rule: {r.name}")
        print(f"  Assign Condition: {r.assign_condition}")
        print(f"  Unassign Condition: {r.unassign_condition}")
        print(f"  Rule Type: {r.rule}")
        print(f"  Field: {r.field}")
        
        # Users are in tabAssignment Rule User
        users = frappe.get_all("Assignment Rule User", filters={"parent": r.name}, fields=["user"])
        print(f"  Users: {[u.user for u in users]}")

if __name__ == "__main__":
    frappe.connect()
    run()
