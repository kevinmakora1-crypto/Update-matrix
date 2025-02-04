import frappe


def execute():
    frappe.db.sql("""
            UPDATE `tabOperations Shift`
            SET status = "Inactive"
            WHERE status = "Not Active"
    """)