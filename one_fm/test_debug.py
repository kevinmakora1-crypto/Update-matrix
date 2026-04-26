import frappe

def run():
    doc = frappe.get_doc("Employee Resignation Extension", "HR-ERE-2026-04-00009")
    rule = frappe.get_doc("Assignment Rule", "Employee Resignation Extension - Pending Operations Manager")
    
    print("Assign Condition Eval:", rule.safe_eval("assign_condition", doc.as_dict()))
    
    user = rule.get_user(doc.as_dict())
    print("Target User:", user)
    
    if user:
        from frappe.desk.form import assign_to
        assign_to.add(
            dict(
                assign_to=[user],
                doctype=doc.get("doctype"),
                name=doc.get("name"),
                description=frappe.render_template(rule.description, doc.as_dict()),
                assignment_rule=rule.name,
                notify=True
            ),
            ignore_permissions=True,
        )
        print("Manual assign_to.add succeeded")
