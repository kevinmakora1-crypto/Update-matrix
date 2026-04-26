import frappe

def run():
    doc = frappe.get_doc("Employee Resignation Extension", "HR-ERE-2026-04-00009")
    rule = frappe.get_doc("Assignment Rule", "Employee Resignation Extension - Pending Operations Manager")

    eval_globals = {"doc": doc, "frappe": frappe}
    try:
        print(f"Condition Eval: {frappe.safe_eval(rule.assign_condition, eval_globals)}")
    except Exception as e:
        print(f"Assign Error: {e}")
        
    try:
        print(f"Unassign Eval: {frappe.safe_eval(rule.unassign_condition, eval_globals)}")
    except Exception as e:
        print(f"Unassign Error: {e}")
        
    print(f"OM value: {doc.operations_manager}")
    print(f"OM valid user: {frappe.db.exists('User', doc.operations_manager)}")
    print("Executing apply_unassign and apply_assign manually...")
    if hasattr(rule, 'apply_unassign'):
        rule.apply_unassign(doc)
    if hasattr(rule, 'apply'):
        rule.apply(doc)
        print("Applied successfully.")
