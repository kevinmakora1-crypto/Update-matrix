# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ClientInterviewShortlist(Document):
	def on_submit(self):
		self.create_employee_schedule_for_client_interview()

	def create_employee_schedule_for_client_interview(self):
		for employee_details in self.client_interview_employee:
			# Delete existing schedule on the same date with conflicting availability
			existing_schedules = frappe.get_all(
				"Employee Schedule",
				filters={
					"employee": employee_details.employee,
					"date": self.interview_date,
					"employee_availability": ["in", ["Working", "Day Off", "Client Day Off", "On The Job Training"]],
				},
				fields=["name"],
			)
			for schedule in existing_schedules:
				frappe.delete_doc("Employee Schedule", schedule.name, ignore_permissions=True)

			# Create a new schedule for the client interview
			employee_schedule = frappe.new_doc("Employee Schedule")
			employee_schedule.employee = employee_details.employee
			employee_schedule.date = self.interview_date
			employee_schedule.employee_availability = "Client Interview"
			employee_schedule.project = self.project
			employee_schedule.insert(ignore_permissions=True)
