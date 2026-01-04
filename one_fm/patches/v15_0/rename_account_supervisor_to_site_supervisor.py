import frappe

def execute():
    doctype_name = "Operations Site"
    
    if not frappe.db.has_column(doctype_name, "account_supervisor"):
        return
    
    frappe.db.sql("""
        UPDATE `tabOperations Site`
        SET site_supervisor = account_supervisor
        WHERE account_supervisor IS NOT NULL
    """)

    frappe.db.sql("""
        UPDATE `tabOperations Site`
        SET site_supervisor_name = account_supervisor_name
        WHERE account_supervisor_name IS NOT NULL
    """)
    
    frappe.db.commit()
