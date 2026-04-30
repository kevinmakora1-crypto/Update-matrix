import frappe

def execute():
    # Rename Child Table first
    if frappe.db.exists("DocType", "Employee Resignation Extension Item"):
        print("Renaming Child Table...")
        frappe.rename_doc("DocType", "Employee Resignation Extension Item", "Employee Resignation Date Adjustment Item", force=True)
    
    # Rename Parent Table
    if frappe.db.exists("DocType", "Employee Resignation Extension"):
        print("Renaming Parent Table...")
        frappe.rename_doc("DocType", "Employee Resignation Extension", "Employee Resignation Date Adjustment", force=True)
    
    # Update Naming Series for the new DocType
    if frappe.db.exists("DocType", "Employee Resignation Date Adjustment"):
        doc = frappe.get_doc("DocType", "Employee Resignation Date Adjustment")
        doc.autoname = "HR-ERDA-.YYYY.-.MM.-.####"
        doc.save(ignore_permissions=True)
        print("Updated Naming Series to HR-ERDA-")

    # Re-export fixtures if needed (not strictly required if in dev mode, it renames files)
    frappe.db.commit()
