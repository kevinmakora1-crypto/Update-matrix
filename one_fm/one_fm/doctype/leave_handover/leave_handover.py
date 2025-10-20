# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from collections import Counter

class LeaveHandover(Document):
	def validate(self):
		if not self.handover_items:
			frappe.throw(_("No responsibilities found for {0}").format(self.employee_name))

	def before_save(self):
		self.status = "Pending"

	def on_submit(self):
		no_reliever_rows = []
		not_accepted_rows = []

		for item in self.handover_items:
			if not item.reliever:
				no_reliever_rows.append(str(item.idx))

			if item.status != "Accepted":
				not_accepted_rows.append(str(item.idx))

		if no_reliever_rows:
			frappe.throw(
				msg=_("Ensure to set the reliever in row(s) {0} and then proceed").format(", ".join(no_reliever_rows)),
				title=_("No Reliever Set")
			)

		if not_accepted_rows:
			frappe.throw(
				msg=_("Ensure that the reliever in row(s) {0} has accepted and update the status.").format(", ".join(not_accepted_rows)),
				title=_("Not Accepted")
			)

		# On submit logic to replace employee with reliever
		# This part requires clarification on which field to update in the referenced doctypes.
		# for item in self.handover_items:
		# 	frappe.db.set_value(item.reference_doctype, item.reference_docname, 'employee_field_name', item.reliever)
		pass
