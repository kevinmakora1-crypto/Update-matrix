# Copyright (c) 2024, one_fm and contributors
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

@frappe.whitelist()
def get_handover_data(leave_application):
	handover_items = []
	leave_application_doc = frappe.get_doc("Leave Application", leave_application)
	employee = leave_application_doc.employee

	# Fetch projects
	projects = frappe.get_all(
		"Project",
		filters={"status": "Open", "account_manager": employee},
		fields=["name"],
	)
	for project in projects:
		handover_items.append({
			"reference_doctype": "Project",
			"reference_docname": project.name,
		})

	# Fetch operations sites
	sites = frappe.get_all(
		"Operations Site",
		filters={"status": "Active", "account_supervisor": employee},
		fields=["name"],
	)
	for site in sites:
		handover_items.append({
			"reference_doctype": "Operations Site",
			"reference_docname": site.name,
		})

	# Fetch process tasks
	tasks = frappe.get_all(
		"Process Task",
		filters={"is_active": 1, "employee": employee},
		fields=["name"],
	)
	for task in tasks:
		handover_items.append({
			"reference_doctype": "Process Task",
			"reference_docname": task.name,
		})

	# Fetch employees reporting to the leave applicant
	employees = frappe.get_all(
		"Employee",
		filters={"status": ("in", ["Active", "Vacation"]), "reports_to": employee},
		fields=["name"],
	)
	for emp in employees:
		handover_items.append({
			"reference_doctype": "Employee",
			"reference_docname": emp.name,
		})

	return {
		"employee": leave_application_doc.employee,
		"employee_name": leave_application_doc.employee_name,
		"leave_application": leave_application_doc.name,
		"leave_start_date": leave_application_doc.from_date,
		"resumption_date": leave_application_doc.resumption_date,
		"handover_items": handover_items,
	}
