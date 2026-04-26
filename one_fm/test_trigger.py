import frappe
from frappe.automation.doctype.assignment_rule.assignment_rule import apply
def run():
    try:
        doc = frappe.get_doc("Employee Resignation Extension", "HR-ERE-2026-04-00009")
        apply(doc)
        frappe.db.commit()
        print("Applied assignment rules.")
        
        # check if assigned
        from frappe.desk.form.assign_to import get
        print("Assignments:", get(dict(doctype=doc.doctype, name=doc.name)))
    except Exception as e:
        print("Error:", e)
