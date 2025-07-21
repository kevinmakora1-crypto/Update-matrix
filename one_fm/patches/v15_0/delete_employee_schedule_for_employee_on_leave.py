import frappe
from frappe.utils import getdate


def execute():
    # Define the range for July 1 to July 31
    from_date = getdate("2025-07-01")
    to_date = getdate("2025-07-31")

    # Get all employees on approved annual leave during July
    leave_apps = frappe.db.get_all(
        "Leave Application",
        filters={
            "status": "Approved",
            "leave_type": "Annual Leave",
            "to_date": [">=", from_date],
            "from_date": ["<=", to_date],
        },
        fields=["employee", "from_date", "to_date"]
    )

    for leave in leave_apps:
        # Get the actual overlap between the leave and July range
        leave_start = max(getdate(leave.from_date), from_date)
        leave_end = min(getdate(leave.to_date), to_date)

        # Delete Employee Schedule records within this range
        frappe.db.sql(
            '''
            DELETE FROM `tabEmployee Schedule`
            WHERE employee = %s
            AND date BETWEEN %s AND %s
            ''',
            (leave.employee, leave_start, leave_end)
        )

    frappe.db.commit()
