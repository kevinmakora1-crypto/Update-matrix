# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class ClientInterviewShortlist(Document):
	def on_submit(self):
		self.create_employee_schedule_for_client_interview()

	def create_employee_schedule_for_client_interview(self):
		for interview_employee in self.client_interview_employee:
			# Delete existing schedule on the same date with conflicting availability
			employee_availability_list = ["Working", "Day Off", "Client Day Off", "On-the-job Training"]
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
			"reference_docname": self.name,
			"project": self.project
		})
		employee_schedule.insert(ignore_permissions=True)

	def on_update_after_submit(self):
		self.mark_attendance_for_interviewed_employees()

	def mark_attendance_for_interviewed_employees(self):
		for interview_employee in self.client_interview_employee:
			if not interview_employee.has_value_changed("attended"):
				continue

			status = "Client Interview" if interview_employee.attended else "Absent"
			attendance_roster_type = "Over-Time" if interview_employee.previous_employee_availability == "Day Off" else "Basic"
			self.mark_attendance(interview_employee.employee, status, attendance_roster_type)

	@frappe.whitelist()
	def mark_attendance(self, employee, status, roster_type):
		attendance = frappe.db.exists("Attendance", {
			"employee": employee,
			"attendance_date": self.interview_date,
			"document_status": ["!=", 2]
		})

		if attendance:
			frappe.db.set_value("Attendance", attendance, "status", status)
			frappe.db.set_value("Attendance", attendance, "roster_type", roster_type)
			frappe.db.set_value("Attendance", attendance, "reference_doctype", self.doctype)
			frappe.db.set_value("Attendance", attendance, "reference_docname", self.name)
			frappe.msgprint(f"Attendance updated for {employee} on {self.interview_date}")
		else:
			doc = frappe.new_doc("Attendance")
			doc.employee = employee
			doc.attendance_date = self.interview_date
			doc.status = status
			doc.roster_type = roster_type
			doc.reference_doctype = self.doctype
			doc.reference_docname = self.name
			doc.insert(ignore_permissions=True)
			doc.submit()
			frappe.msgprint(f"Attendance created for {employee} on {self.interview_date}")

	def on_cancel(self):
		self.check_if_interview_date_is_in_the_past()
		self.delete_employee_schedule_and_attendance()

	def check_if_interview_date_is_in_the_past(self):
		if getdate(self.interview_date) < getdate(today()):
			frappe.throw("Cannot cancel a client interview shortlist with a past interview date.")

	def delete_employee_schedule_and_attendance(self):
		self.delete_employee_schedule()
		self.cancel_attendance()

	def delete_employee_schedule(self):
		schedules = frappe.get_all(
			"Employee Schedule",
			filters={
				"date": self.interview_date,
				"reference_doctype": self.doctype,
				"reference_docname": self.name,
			},
		)
		for schedule in schedules:
			frappe.delete_doc("Employee Schedule", schedule.name, ignore_permissions=True)

	def cancel_attendance(self):
		attendances = frappe.get_all(
			"Attendance",
			filters={
				"attendance_date": self.interview_date,
				"reference_doctype": self.doctype,
				"reference_docname": self.name,
			},
		)
		for attendance in attendances:
			frappe.get_doc("Attendance", attendance.name).cancel()
