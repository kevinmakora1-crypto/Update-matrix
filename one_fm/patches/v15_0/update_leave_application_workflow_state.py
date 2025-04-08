import frappe


def execute():
    frappe.db.sql("""
        UPDATE
            `tabLeave Application`
        SET
            workflow_state = 'Pending Approval'
        WHERE
            workflow_state = 'Open'
    """)
