# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class ClientEvent(Document):
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
