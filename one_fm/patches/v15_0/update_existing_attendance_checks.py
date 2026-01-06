import frappe
from one_fm.utils import get_approver_user

def execute():
    attendance_checks = frappe.get_all(
        "Attendance Check",
        filters={"workflow_state": "Pending Approval"},
        fields=["name", "employee"],
    )
    for check in attendance_checks:
        approver = get_approver_user(check.employee)
        if approver:
            frappe.db.set_value("Attendance Check", check.name, "approver", approver)
