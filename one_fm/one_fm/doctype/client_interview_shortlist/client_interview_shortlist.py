# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ClientInterviewShortlist(Document):
	def on_submit(self):
		self.create_employee_schedule_for_client_interview()

	def create_employee_schedule_for_client_interview(self):
		for interview_employee in self.client_interview_employee:
			# Delete existing schedule on the same date with conflicting availability
			employee_availability_list = ["Working", "Day Off", "Client Day Off", "On The Job Training"]
			self.delete_existing_employee_schedules(interview_employee, employee_availability_list)
			self.create_employee_schedule(interview_employee.employee, interview_employee.roster_type)

	def delete_existing_employee_schedules(self, interview_employee, employee_availability_list):
		existing_schedules = frappe.get_all(
			"Employee Schedule",
			filters={
				"employee": interview_employee.employee,
				"date": self.interview_date,
				"employee_availability": ["in", employee_availability_list],
			},
			fields=["name", "employee_availability"]
		)
		for schedule in existing_schedules:
			frappe.delete_doc("Employee Schedule", schedule.name, ignore_permissions=True)
			frappe.db.set_value("Client Interview Employee", interview_employee.name, "previous_employee_availability", schedule.employee_availability)

	def create_employee_schedule(self, employee, roster_type):
		employee_schedule = frappe.get_doc({
			"doctype": "Employee Schedule",
			"employee": employee,
			"date": self.interview_date,
			"employee_availability": "Client Interview",
			"roster_type": roster_type,
			"reference_doctype": self.doctype,
			"reference_name": self.name,
			"project": self.project
		})
		employee_schedule.insert(ignore_permissions=True)

	def on_update_after_submit(self):
		self.mark_attendance_for_interviewed_employees()

	def mark_attendance_for_interviewed_employees(self):
		for interview_employee in self.client_interview_employee:
			if not interview_employee.has_value_changed("attended"):
				continue

			status = "Present" if interview_employee.attended else "Absent"
			attendance_roster_type = "Over-Time" if interview_employee.previous_employee_availability == "Day Off" else "Basic"
			self.mark_attendance(interview_employee.employee, status, attendance_roster_type)

	@frappe.whitelist()
	def mark_attendance(self, employee, status, roster_type):
		attendance = frappe.db.exists("Attendance", {
			"employee": employee,
			"attendance_date": self.interview_date
		})

		if attendance:
			frappe.db.set_value("Attendance", attendance, "status", status)
			frappe.db.set_value("Attendance", attendance, "roster_type", roster_type)
			frappe.msgprint(f"Attendance updated for {employee} on {self.interview_date}")
		else:
			doc = frappe.new_doc("Attendance")
			doc.employee = employee
			doc.attendance_date = self.interview_date
			doc.status = status
			doc.roster_type = roster_type
			doc.insert(ignore_permissions=True)
			frappe.msgprint(f"Attendance created for {employee} on {self.interview_date}")
