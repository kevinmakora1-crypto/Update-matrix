# Copyright (c) 2025, omar jaber and contributors
# For license information, please see license.txt
from datetime import date, timedelta

import frappe
from frappe.model.document import Document

from one_fm.api.v1.utils import response


class EmployeeWeeklyAction(Document):
	pass


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
        fields = ["name", "type"] if is_current else ["name", "date", "type"]

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






