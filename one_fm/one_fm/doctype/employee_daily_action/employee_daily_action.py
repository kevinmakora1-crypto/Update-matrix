# Copyright (c) 2025, omar jaber and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeDailyAction(Document):
	def create_blockers(self):
		"Create blockers for the employee from the blockers table"
		for blocker in self.blocker_table:
			blocker_doc = frappe.new_doc("Blocker")
			blocker_doc.user = self.employee_email
			blocker_doc.assigned_to = self.manager_email
			blocker_doc.priority = blocker.priority
			blocker_doc.date = self.date
			blocker_doc.status = "Open"
			blocker_doc.blocker_details = blocker.problem
			blocker_doc.save()
			frappe.db.commit()


	def on_submit(self):
		self.create_blockers()
	
