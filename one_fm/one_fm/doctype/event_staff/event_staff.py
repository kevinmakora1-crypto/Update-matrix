# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days, date_diff, add_days
import datetime

class EventStaff(Document):
	def validate(self):
		self.validate_date()

	def validate_date(self):
		if getdate(self.end_date) < getdate(self.start_date):
			frappe.throw("End Date cannot be before Start Date.")
		if not self.start_datetime or not self.end_datetime:
			frappe.throw("Start DateTime and End DateTime are mandatory.")
		if frappe.utils.get_datetime(self.end_datetime) <= frappe.utils.get_datetime(self.start_datetime):
			frappe.throw("End DateTime must be after Start DateTime.")

	def on_submit(self):
		self.create_employee_schedule()

	def create_employee_schedule(self):
		start_date = getdate(self.start_date)
		end_date = getdate(self.end_date)
		number_of_days = date_diff(end_date, start_date) + 1  # Include end date
		for i in range(number_of_days):
			date = add_days(start_date, i)
			employee_schedule = frappe.get_doc(
				{
					"doctype": "Employee Schedule",
					"employee": self.employee,
					"date": date,
					"shift": self.operations_shift,
					"shift_type": self.shift_type,
					"operations_role": self.operations_role,
					"employee_availability": 'Working',
					"roster_type": self.roster_type,
					"site": self.site,
					"project": self.project,
					"reference_doctype": self.doctype,
					"reference_docname": self.name,
					"is_event_schedule": 1,
					"event_staff": self.name,
					"day_off_ot": self.day_off_ot,
					"start_datetime": self.get_event_start_end_date_time().get("start_datetime"),
					"end_datetime": self.get_event_start_end_date_time().get("end_datetime")
				}
			)
			employee_schedule.save(ignore_permissions=True)

	def get_event_start_end_date_time(self, date=None):
		start_time = frappe.utils.get_datetime(self.start_datetime).time()
		end_time = frappe.utils.get_datetime(self.end_datetime).time()
		start_datetime = datetime.datetime.combine(getdate(date), start_time)
		if end_time < start_time:
			end_date = add_days(getdate(date), 1)
		else:
			end_date = getdate(date)
		end_datetime = datetime.datetime.combine(end_date, end_time)
		return {
			"start_datetime": start_datetime,
			"end_datetime": end_datetime
		}