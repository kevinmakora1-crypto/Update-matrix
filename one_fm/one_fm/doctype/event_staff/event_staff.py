# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days, date_diff, add_days
import datetime

class EventStaff(Document):
	def validate(self):
		self.validate_date()
		self.validate_staffing_requirement()
		self.validate_overlapping_event_staff()

	def validate_overlapping_event_staff(self):
		# Only check for new documents (not submitted yet)
		if not self.employee or not self.client_event or not self.start_date or not self.end_date or not self.operations_role:
			return
		overlapping = frappe.db.sql(
			"""
			SELECT
				name, start_date, end_date FROM `tabEvent Staff`
			WHERE
				employee = %(employee)s AND docstatus < 2 AND name != %(name)s
				AND (
					(start_date <= %(end_date)s AND end_date >= %(start_date)s)
				)
			""",
			{
				"employee": self.employee,
				"start_date": self.start_date,
				"end_date": self.end_date,
				"name": self.name or ""
			},
			as_dict=True
		)
		if overlapping:
			msg = f"{self.employee} already assigned to {self.operations_role} from {overlapping[0]['start_date']} to {overlapping[0]['end_date']}."
			frappe.throw(msg)

	def validate_staffing_requirement(self):
		if not self.client_event or not self.operations_role:
			return
		requirements = self.get_event_staffing_requirement()
		if not requirements:
		    return
		filters = {
			"client_event": self.client_event,
			"operations_role": self.operations_role,
			"docstatus": ["<", 2]
		}
		assigned_count = frappe.db.count("Event Staff", filters)
		if assigned_count > requirements:
			frappe.throw(f"The number of assigned staff for Operations Role {self.operations_role} exceeds the required count {requirements}.")

	def get_event_staffing_requirement(self):
		if not self.client_event or not self.operations_role:
			return 0
		requirement = frappe.db.get_value(
			"Client Event Staff Requirement",
			{
				"parent": self.client_event,
				"parenttype": "Client Event",
				"operation_role": self.operations_role
			},
			"count"
		)
		return requirement or 0

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
			start_end_datetime = self.get_event_start_end_date_time(date)
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
					"start_datetime": start_end_datetime.get("start_datetime"),
					"end_datetime": start_end_datetime.get("end_datetime")
				}
			)
			employee_schedule.save(ignore_permissions=True)

			if not self.shift_type:
				self.create_shift_assignment_for_employee_schedule(employee_schedule, self.event_location)

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

	def create_shift_assignment_for_employee_schedule(self, employee_schedule, event_location):
		shift_assignment = frappe.get_doc(
			{
				"doctype": "Shift Assignment",
				"employee": employee_schedule.employee,
				"employee_name": employee_schedule.employee_name,
				"start_date": employee_schedule.start_datetime.date(),
				"end_date": employee_schedule.end_datetime.date(),
				"shift": employee_schedule.shift,
				"employee_schedule": employee_schedule.name,
				"site": employee_schedule.site,
				"project": employee_schedule.project,
				"is_event_based_shift": 1,
				"event_staff": self.name,
				"start_datetime": employee_schedule.start_datetime,
				"end_datetime": employee_schedule.end_datetime,
				"site_location": event_location
			}
		)
		shift_assignment.insert(ignore_permissions=True)
		shift_assignment.submit()