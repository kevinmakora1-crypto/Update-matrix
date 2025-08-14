# Copyright (c) 2025, omar jaber and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days, today

from one_fm.processor import sendemail
from one_fm.utils import  get_approver, get_approver

class EmployeeDailyAction(Document):
	def validate(self):
		self.validate_manager()
		self.fetch_todos()


	def fetch_todos(self):
		""" Fetch all the todos for the employee for the current date """

		if not self.todays_plan_and_accomplishments: #If created from console
			todays_todos = frappe.db.get_all("ToDo", {"allocated_to": self.employee_email, "date": self.date},['reference_name', 'reference_type', 'name', 'status','description','type'])
			for todo in todays_todos:
				row = self.append("todays_plan_and_accomplishments")
				row.todo = todo.name
				row.todo_type = todo.type
				row.reference_type = todo.reference_type
				row.reference = todo.reference_name
				row.planned = 0
				row.description = todo.description
				row.completed = 1 if todo.status != "Open" else 0

		if not self.tomorrows_plan: #If created from console
			tomorrows_todos = frappe.db.get_all("ToDo", {"allocated_to": self.employee_email, "date": add_days(getdate(self.date),1)},['reference_name', 'reference_type', 'name', 'status','description','type'])
			for todo in tomorrows_todos:
				row = self.append("tomorrows_plan")
				row.todo = todo.name
				row.description = todo.description
				row.todo_type = todo.type
				row.reference_type = todo.reference_type
				row.reference = todo.reference_name


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
			blocker_doc.reference_doctype = self.doctype
			blocker_doc.reference_name = self.name
			blocker_doc.save(ignore_permissions=True)
			frappe.db.commit()

	def  validate_manager(self):
		"""Ensure that a manager is set from the shift,site or reports to field """
		reports_to = get_approver(self.employee)
		if not reports_to:
			frappe.throw(f"No Reports to set for {self.employee_name}")
		self.reports_to = reports_to



	def on_submit(self):
		self.create_blockers()


class NotifyReportsToOnAbsenceOfReport:

	def __init__(self):
		self.yesterday = add_days(today(), -1)
		self.non_compliant_employees = self.fetch_non_compliant_employees

	@property
	def fetch_yesterday_reports_employee(self):
		return frappe.db.get_list("Employee Daily Action", filters={"date": self.date, "docstatus": 1}, pluck="employee")
	
	@property
	def fetch_non_compliant_employees(self):
		return frappe.db.get_list("Employee", filters={
			"status": "Active",
			"is_in_ows": "Yes",
			"name": ["NOT IN", self.fetch_yesterday_reports_employee],
		},
		fields=["name", "attendance_by_timesheet", "shift_working", "holiday_list", "employee_name"]
		)
	

	@property
	def shift_working_employee_schedule(self):
		shift_working_employees = [obj.name for obj in self.non_compliant_employees if obj.shift_working]
		return frappe.db.get_all("Employee Schedule", filters={
			"date": self.yesterday,
			"employee": ["IN", shift_working_employees],
			"employee_availability": "Working",
		}, pluck="employee")
	
	@property
	def leave_attendance(self):
		attendance_employees = [obj.name for obj in self.non_compliant_employees if not obj.shift_working]
		return frappe.db.get_all("Attendance", filters={
			"date": self.yesterday,
			"status": "On Leave",
			"employee": ["IN", attendance_employees]
		}, pluck="employee")
	
	
	@property
	def yesterday_holiday_status(self):
		holidays = {obj.holiday_list for obj in self.non_compliant_employees if not obj.shift_working}
		holiday_lists = frappe.get_all(
			"Holiday List",
			filters=[
				["Holiday", "holiday_date", "=", self.yesterday],
				["name", "in", list(holidays)]
			],
			fields=["name", "holiday_list_name"]
		)
		return holiday_lists
	

	
	def send_notification_mail(self, recipient, employee_name):
		msg = frappe.render_template('one_fm/templates/emails/employee_daily_action_check.html', 
							   context={"employee_name": employee_name, "yesterday": self.yesterday})
		sender = frappe.get_value("Email Account", filters = {"default_outgoing": 1}, fieldname = "email_id") or None
		sendemail(sender=sender, recipients= recipient,
            content=msg, subject="Employee Daily Action Check", delayed=False, is_scheduler_email=True)


	def notify_employee(self):
		if self.non_compliant_employees:
			employee_schedules = self.shift_working_employee_schedule
			leave_attendance = self.leave_attendance
			holiday_status = self.yesterday_holiday_status

			for obj in self.non_compliant_employees:
				if obj.shift_working:
					if obj.name in employee_schedules:
						self.send_notification_mail(employee_name=obj.employee_name)
				else:
					if obj.holiday_list not in holiday_status and  obj.name not in leave_attendance:
						self.send_notification_mail(employee_name=obj.employee_name)




		