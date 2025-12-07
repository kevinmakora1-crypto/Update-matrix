# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days, date_diff, today
import datetime

class EventStaff(Document):
	def validate(self):
		self.validate_date()
		self.validate_staffing_requirement()
		self.validate_overlapping_event_staff()

	def validate_date(self):
		if getdate(self.end_date) < getdate(self.start_date):
			frappe.throw("End Date cannot be before Start Date.")
		if not self.start_datetime or not self.end_datetime:
			frappe.throw("Start DateTime and End DateTime are mandatory.")
		if frappe.utils.get_datetime(self.end_datetime) <= frappe.utils.get_datetime(self.start_datetime):
			frappe.throw("End DateTime must be after Start DateTime.")

	def validate_staffing_requirement(self):
		if not self.client_event or not self.designation:
			return
		requirements = self.get_event_staffing_requirement()
		if not requirements:
			return
		filters = {
			"client_event": self.client_event,
			"designation": self.designation,
			"docstatus": ["<", 2]
		}
		assigned_count = frappe.db.count("Event Staff", filters)
		if assigned_count > requirements:
			frappe.throw(f"The number of assigned staff for Designation {self.designation} exceeds the required count {requirements}.")

	def get_event_staffing_requirement(self):
		if not self.client_event or not self.designation:
			return 0
		requirement = frappe.db.get_value(
			"Client Event Staff Requirement",
			{
				"parent": self.client_event,
				"parenttype": "Client Event",
				"designation": self.designation
			},
			"count"
		)
		return requirement or 0

	def validate_overlapping_event_staff(self):
		if not self.employee or not self.client_event or not self.start_date or not self.end_date or not self.designation:
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
			msg = f"{self.employee} already assigned to {self.designation} from {overlapping[0]['start_date']} to {overlapping[0]['end_date']}."
			frappe.throw(msg)

	def on_submit(self):
		self.process_employee_schedules()

	def process_employee_schedules(self, start_date=None):
		start_date = getdate(start_date) if start_date else getdate(self.start_date)
		end_date = getdate(self.end_date)
		existing_schedules = get_existing_schedules(self.employee, start_date, end_date)
		existing_schedules_map = { frappe.utils.getdate(d.date): d.name for d in existing_schedules }

		number_of_days = date_diff(end_date, start_date) + 1

		for i in range(number_of_days):
			current_date = add_days(start_date, i)
			start_end_datetime = self.get_event_start_end_date_time(current_date)
			employee_schedule_data = self.get_schedule_data(start_end_datetime, current_date)

			if current_date in existing_schedules_map:
				schedule_doc = frappe.get_doc("Employee Schedule", existing_schedules_map[current_date])
				schedule_doc.update(employee_schedule_data)
				schedule_doc.save(ignore_permissions=True)
			else:
				new_schedule = frappe.new_doc("Employee Schedule")
				new_schedule.update(employee_schedule_data)
				new_schedule.insert(ignore_permissions=True)

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

	def get_schedule_data(self, start_end_datetime, current_date):
		return {
			"employee": self.employee,
			"date": current_date,
			"employee_availability": "Client Event",
			"is_event_schedule": 1,
			"event_staff": self.name,
			"shift": self.operations_shift,
			"shift_type": self.shift_type,
			"project": self.project,
			"site": self.site,
			"start_datetime": start_end_datetime.get("start_datetime"),
			"end_datetime": start_end_datetime.get("end_datetime"),
			"designation": self.designation,
			"roster_type": self.roster_type,
			"day_off_ot": self.day_off_ot,
			"client_event": self.client_event,
			"event_location": self.event_location,
			"reference_doctype": "Event Staff",
			"reference_docname": self.name,
			"operations_role": None,
			"post_abbrv": None,
		}

	def on_update_after_submit(self):
		old_doc = self.get_doc_before_save()
		if getdate(self.end_date) < getdate(old_doc.end_date):
			self.delete_employee_schedules(self.end_date)
		elif getdate(self.end_date) > getdate(old_doc.end_date):
			new_start_date = add_days(getdate(old_doc.end_date), 1)
			conflicting_dates = get_conflicting_dates(self.employee, new_start_date, self.end_date)
			if conflicting_dates:
				frappe.throw(f"Cannot extend the event as there are conflicting schedules on the following dates: {', '.join(conflicting_dates)}")

			self.process_employee_schedules(start_date=new_start_date)

	def delete_employee_schedules(self, date):
		frappe.db.delete(
			"Employee Schedule",
			{
				"event_staff": self.name,
				"date": [">", getdate(date)]
			}
		)

	def on_cancel(self):
		self.delete_employee_schedules(today())

@frappe.whitelist()
def get_conflicting_dates(employee, start_date, end_date):
	if not employee or not start_date or not end_date:
		return []

	conflicting_schedules = get_existing_schedules(employee, start_date, end_date)

	return [schedule.get("date").strftime("%Y-%m-%d") for schedule in conflicting_schedules]

def get_existing_schedules(employee, start_date, end_date):
	return frappe.get_all(
		"Employee Schedule",
		filters={
			"employee": employee,
			"docstatus": ("!=", 2),
			"date": ["between", [start_date, end_date]]
		},
		fields=["name", "date"]
	)