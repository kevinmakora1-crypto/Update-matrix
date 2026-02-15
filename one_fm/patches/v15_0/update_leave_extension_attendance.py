import frappe


def execute():
    """Update attendance for Leave Extension Requests created after 2026-01-20"""
    
    leave_extension_requests = frappe.get_all(
        "Leave Extension Request",
        filters={
            "creation": [">=", "2026-01-20"],
            "docstatus": 1
        },
        fields=["name", "leave_application"]
    )
    
    for ler in leave_extension_requests:
        try:
            if ler.leave_application:
                leave_app = frappe.get_doc("Leave Application", ler.leave_application)
                leave_app.update_attendance()
                frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Error in {ler.name}: {str(e)}", "Leave Extension Attendance Update")
            frappe.db.rollback()