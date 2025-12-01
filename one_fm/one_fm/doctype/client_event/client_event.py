# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime
import json

class ClientEvent(Document):
	def validate(self):
		now = now_datetime()

		# Rule 1: Start Date or Start Datetime must be in the future
		if self.start_date and get_datetime(self.start_date) < now:
			frappe.throw("The scheduled event time must be a future date/time. Please adjust the event details.")
		if self.event_start_datetime and get_datetime(self.event_start_datetime) < now:
			frappe.throw("The scheduled event time must be a future date/time. Please adjust the event details.")

		# Rule 2: End Date or End Datetime must be in the future
		if self.end_date and get_datetime(self.end_date) < now:
			frappe.throw("The scheduled end date/time must be a future date/time. Please adjust the event details.")
		if self.event_end_datetime and get_datetime(self.event_end_datetime) < now:
			frappe.throw("The scheduled end date/time must be a future date/time. Please adjust the event details.")

		# Rule 3: End must be after Start
		if self.start_date and self.end_date and get_datetime(self.end_date) < get_datetime(self.start_date):
			frappe.throw("The scheduled end date/time must be later than Start Date or Start Datetime. Please adjust the event details.")
		if self.event_start_datetime and self.event_end_datetime and get_datetime(self.event_end_datetime) < get_datetime(self.event_start_datetime):
			frappe.throw("The scheduled end date/time must be later than Start Date or Start Datetime. Please adjust the event details.")

	@frappe.whitelist()
	def add_event_staff(self, staff):
		staff_data = json.loads(staff)
		for record in staff_data:
			doc = frappe.new_doc("Event Staff")
			doc.client_event = self.name
			doc.employee = record.get("employee")
			doc.operations_role = record.get("operations_role")
			doc.roster_type = record.get("roster_type")
			doc.day_off_ot = record.get("day_off_ot")
			doc.operations_shift = record.get("operations_shift")
			doc.save(ignore_permissions=True)
			doc.submit()
