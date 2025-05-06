# Copyright (c) 2025, omar jaber and contributors
# For license information, please see license.txt
from datetime import date, timedelta

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime

from one_fm.api.v1.utils import response


class EmployeeWeeklyAction(Document):
	

	def on_submit(self):
		self.create_blockers()

	def create_blockers(self):
		if not self.blockers:
			return

		for blocker in self.blockers:
			doc = frappe.new_doc("Blocker")
			doc.user = frappe.session.user
			doc.date = get_datetime().date()
			doc.assigned_to = self.get_reporting_manager()
			doc.priority = blocker.priority
			doc.blocker_details = blocker.problem
			doc.reference_doctype = self.doctype
			doc.reference_name = self.name
			doc.insert(ignore_permissions=True)

		frappe.db.commit()


	def get_reporting_manager(self):
		employee_id = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "reports_to")
		return frappe.db.get_value("Employee", employee_id, "user_id") if employee_id else None

			
	


def get_week_dates(offset=0):
    """Get dates from Sunday to Saturday for a given week offset.
    offset=0 → current week, offset=1 → next week, etc.
    """
    today = date.today()
    weekday = today.weekday()
    start_of_week = today - timedelta(days=weekday + 1 if weekday != 6 else 0) + timedelta(weeks=offset)
    return [(start_of_week + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]


@frappe.whitelist()
def fetch_todos(is_current: bool = True):
    try:
        dates = get_week_dates(offset=0 if is_current else 1)
        fields = ["name", "type", "description"]
        if not is_current:
            fields.extend(["date", "reference_name"])
        

        week_todos = frappe.db.get_list(
            "ToDo",
            filters={
                "date": ["in", dates],
                "allocated_to": frappe.session.user
            },
            fields=fields
        )

        return response("Success", 200, week_todos)

    except Exception:
        frappe.log_error(
            title="Error fetching ToDo on employee weekly report",
            message=frappe.get_traceback()
        )
        return response("Error", 400)






