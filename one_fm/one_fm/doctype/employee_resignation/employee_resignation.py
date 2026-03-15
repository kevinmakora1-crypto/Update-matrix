# Copyright (c) 2026, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EmployeeResignation(Document):
	def validate(self):
		self.set_supervisor()

	def before_save(self):
		self.set_supervisor()

	def set_supervisor(self):
		"""
		Automatically populate the Supervisor (User) field based on:
		1. Employee's Reports To → linked Employee's user_id
		2. Employee's Site → Operations Site's site_supervisor → their user_id
		3. Employee's Project → Project's project_manager → their user_id

		Does nothing if supervisor is already set or employee is not set.
		"""
		if not self.employee or self.supervisor:
			return

		# 1. Reports To
		reports_to = frappe.db.get_value("Employee", self.employee, "reports_to")
		if reports_to:
			user_id = frappe.db.get_value("Employee", reports_to, "user_id")
			if user_id:
				self.supervisor = user_id
				return

		# 2. Site Supervisor
		site = frappe.db.get_value("Employee", self.employee, "site")
		if site:
			site_supervisor = frappe.db.get_value("Operations Site", site, "site_supervisor")
			if site_supervisor:
				user_id = frappe.db.get_value("Employee", site_supervisor, "user_id")
				if user_id:
					self.supervisor = user_id
					return

		# 3. Project Manager
		project = frappe.db.get_value("Employee", self.employee, "project")
		if project:
			project_manager = frappe.db.get_value("Project", project, "project_manager")
			if project_manager:
				user_id = frappe.db.get_value("Employee", project_manager, "user_id")
				if user_id:
					self.supervisor = user_id
