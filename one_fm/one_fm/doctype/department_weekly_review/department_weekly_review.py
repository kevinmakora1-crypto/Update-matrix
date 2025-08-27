# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, timedelta
from frappe.model.document import Document
from frappe.utils import get_datetime


class DepartmentWeeklyReview(Document):
	pass

def get_iso_week_start_end(week, year):
    """
    Returns tuple of (start_datetime, end_datetime) for the given ISO week
    where:
    - start_datetime is Monday 00:00:00 of the week
    - end_datetime is Sunday 23:59:59 of the week
    """
    jan4 = datetime(year, 1, 4)  # January 4 is always in week 1
    week1_monday = jan4 - timedelta(days=jan4.isoweekday()-1)
    monday = week1_monday + timedelta(weeks=week-1)
    
    start_datetime = get_datetime(monday)
    end_datetime = get_datetime(monday + timedelta(days=6, hours=23, minutes=59, seconds=59))
    
    return start_datetime, end_datetime

@frappe.whitelist()
def get_employees_by_department(department):
    return frappe.get_all("Employee",filters={"department": department, "status": "Active"},fields=["name", "employee_name"])

@frappe.whitelist()
def get_blockers_by_department(department, week, year):    
    start_date, end_date = get_iso_week_start_end(int(week), int(year))

    department_employees = frappe.get_all("Employee",filters={"department": department, "status": "Active"},fields=["user_id", "employee_name"])
    
    user_id_to_name = {emp["user_id"]: emp["employee_name"] for emp in department_employees}
    department_user_ids = list(user_id_to_name.keys())

    if not department_user_ids:
        return []

    blockers = frappe.get_all("Blocker",filters={"user": ["in", department_user_ids], "date": ["between", [start_date, end_date]] },fields=["blocker_details", "date", "assigned_to", "user"])

    result = []

    for b in blockers:
        result.append({
            "blocker_details": b["blocker_details"],
            "employee_name": user_id_to_name.get(b["user"], ""),
            "date": b["date"],
            "assigned_to": b["assigned_to"]
        })

    return result


