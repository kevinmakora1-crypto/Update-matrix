# Copyright (c) 2026, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class FormalHearing(Document):
	def has_not_attended_at_all(self):
		"""
		Checks if the employee has not attended the formal hearing at all.
		- If Inside Kuwait: must miss both first and rescheduled hearing.
		- If Outside Kuwait: must miss the first hearing.
		"""
		if self.location_status == "Inside Kuwait":
			return self.did_not_attend_first_hearing and self.did_not_attend_rescheduled_hearing
		else:
			return self.did_not_attend_first_hearing

	# def before_workflow_action(self):
	# 	# Additional safety check for workflow redirection
	# 	# This is a fallback if the workflow conditions are not strictly followed
	# 	if self.workflow_state == "Draft" and self.current_workflow_action == "Submit for Review":
	# 		if self.has_not_attended_at_all():
	# 			# We want to ensure it goes to Pending HR Manager
	# 			pass
	# 		else:
	# 			# We want to ensure it goes to Pending Operations Manager
	# 			pass


@frappe.whitelist()
def make_leave_application(source_name: str, leave_type: str | None = None):
	def set_missing_values(source, target):
		if leave_type:
			target.leave_type = leave_type
		target.employee = source.employee
		target.posting_date = frappe.utils.today()

	doc = get_mapped_doc("Formal Hearing", source_name, {
		"Formal Hearing": {
			"doctype": "Leave Application",
			"field_map": {
				"employee": "employee"
			}
		}
	}, target_doc=None, postprocess=set_missing_values)

	return doc


@frappe.whitelist()
def make_employee_resignation(source_name: str):
	def set_missing_values(source, target):
		target.employee = source.employee
		target.relieving_date = frappe.utils.today()
		# Add more mappings as needed from Employee details if not auto-fetched
		employee = frappe.get_doc("Employee", source.employee)
		target.department = employee.department
		target.designation = employee.designation
		target.employment_type = employee.employment_type

	doc = get_mapped_doc("Formal Hearing", source_name, {
		"Formal Hearing": {
			"doctype": "Employee Resignation",
			"field_map": {
				"employee": "employee"
			}
		}
	}, target_doc=None, postprocess=set_missing_values)

	return doc


@frappe.whitelist()
def make_employee_transfer(source_name: str):
	def set_missing_values(source, target):
		target.employee = source.employee
		target.transfer_date = frappe.utils.today()
		# Company is often required
		employee = frappe.get_doc("Employee", source.employee)
		target.company = employee.company

	doc = get_mapped_doc("Formal Hearing", source_name, {
		"Formal Hearing": {
			"doctype": "Employee Transfer",
			"field_map": {
				"employee": "employee"
			}
		}
	}, target_doc=None, postprocess=set_missing_values)

	return doc
