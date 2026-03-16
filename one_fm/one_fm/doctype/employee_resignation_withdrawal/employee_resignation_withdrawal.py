# Copyright (c) 2026, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeResignationWithdrawal(Document):
	def validate(self):
		self.set_approver()

	def set_approver(self):
		if not self.employee:
			return

		employee_details = frappe.db.get_value(
			"Employee", self.employee, ["reports_to", "site", "project"], as_dict=True
		)

		if not employee_details:
			return

		approver_employee = None

		# 1. Reports to
		if employee_details.reports_to:
			approver_employee = employee_details.reports_to

		# 2. Site Supervisor
		if not approver_employee and employee_details.site:
			approver_employee = frappe.db.get_value("Operations Site", employee_details.site, "site_supervisor")

		# 3. Project Manager
		if not approver_employee and employee_details.project:
			approver_employee = frappe.db.get_value("Project", employee_details.project, "project_manager")

		if approver_employee:
			approver_user = frappe.db.get_value("Employee", approver_employee, "user_id")
			if approver_user:
				self.supervisor = approver_user
