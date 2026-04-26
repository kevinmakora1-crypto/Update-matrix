import frappe
from frappe.model.workflow import apply_workflow

def run():
    try:
        frappe.db.set_value("Employee Resignation Extension", "HR-ERE-2026-04-00009", "workflow_state", "Pending Supervisor")
        frappe.db.commit()
        
        doc = frappe.get_doc("Employee Resignation Extension", "HR-ERE-2026-04-00009")
        # Ensure supervisor is assigned
        if doc.supervisor:
            from frappe.desk.form.assign_to import add
            add({
                "assign_to": [doc.supervisor],
                "doctype": doc.doctype,
                "name": doc.name,
                "description": "Supervisor Assignment"
            }, ignore_permissions=True)
            
        print("Before Workflow Action:")
        from frappe.desk.form.assign_to import get
        print("Assignments:", get({"doctype": doc.doctype, "name": doc.name}))
        
        # Apply Accept action
        apply_workflow(doc, "Accept")
        frappe.db.commit()
        
        print("\nAfter Workflow Action:")
        print("Workflow State:", doc.workflow_state)
        print("Assignments:", get({"doctype": doc.doctype, "name": doc.name}))
        
    except Exception as e:
        print("Exception:", e)
