import frappe
from frappe import _

def execute():
    dates = ["2025-11-18", "2025-11-17"]
    attendance_checks = frappe.get_all(
        "Attendance Check",
        filters={
            "date": ["in", dates],
            "docstatus": 0,
            "workflow_state": ["in", ["Pending Approval"]]
        },
        fields=["name"]
    )


    if not attendance_checks:
        frappe.msgprint(_("No pending Attendance Check records found for the specified dates."))
        return

    for ac in attendance_checks:
        try:
            doc = frappe.get_doc("Attendance Check", ac.name)
            if hasattr(doc, "workflow_state"):
                doc.workflow_state = "Approved"

            doc.attendance_status = "Present"
            doc.justification = "Approved by Administrator"
            doc.flags.ignore_mandatory = True
            doc.save(ignore_permissions=True)
            doc.submit()
        except Exception:
            frappe.log_error(title=f"Failed to approve Attendance Check {ac.name}", message=frappe.get_traceback())

