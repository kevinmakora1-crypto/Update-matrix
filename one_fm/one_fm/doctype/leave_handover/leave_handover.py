# Copyright (c) 2024, one_fm and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LeaveHandover(Document):
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
