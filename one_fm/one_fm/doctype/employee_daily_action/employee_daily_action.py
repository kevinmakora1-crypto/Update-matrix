# Copyright (c) 2025, omar jaber and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days, today

from one_fm.processor import sendemail
from one_fm.utils import  get_approver, get_approver_user

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
		self._non_compliant_employees = None
		self._shift_working_schedules = None
		self._leave_attendance = None
		self._holiday_lists = None

	@property
	def non_compliant_employees(self):
		if self._non_compliant_employees is None:
			reported_employees = set(frappe.db.get_list(
				"Employee Daily Action", 
				filters={"date": self.yesterday, "docstatus": 1}, 
				pluck="employee"
			))
			
			all_employees = frappe.db.get_list("Employee", filters={
				"status": "Active",
				"is_in_ows": "Yes",
			}, fields=["name", "attendance_by_timesheet", "shift_working", "holiday_list", "employee_name"])
			
			self._non_compliant_employees = [
				emp for emp in all_employees 
				if emp.name not in reported_employees
			]
		
		return self._non_compliant_employees

	@property
	def shift_working_employee_schedule(self):
		if self._shift_working_schedules is None:
			shift_employees = [emp.name for emp in self.non_compliant_employees if emp.shift_working]
			
			if not shift_employees:
				self._shift_working_schedules = set()
			else:
				self._shift_working_schedules = set(frappe.db.get_all("Employee Schedule", filters={
					"date": self.yesterday,
					"employee": ["IN", shift_employees],
					"employee_availability": "Working",
				}, pluck="employee"))
		
		return self._shift_working_schedules

	@property
	def leave_attendance(self):
		if self._leave_attendance is None:
			non_shift_employees = [emp.name for emp in self.non_compliant_employees if not emp.shift_working]
			
			if not non_shift_employees:
				self._leave_attendance = set()
			else:
				self._leave_attendance = set(frappe.db.get_all("Attendance", filters={
					"attendance_date": self.yesterday,
					"status": "On Leave",
					"employee": ["IN", non_shift_employees]
				}, pluck="employee"))
		
		return self._leave_attendance

	@property
	def yesterday_holiday_status(self):
		if self._holiday_lists is None:
			holiday_lists = {emp.holiday_list for emp in self.non_compliant_employees 
							if not emp.shift_working and emp.holiday_list}
			
			if not holiday_lists:
				self._holiday_lists = set()
			else:
				result = frappe.db.sql("""
					SELECT DISTINCT hl.name
					FROM `tabHoliday List` hl
					INNER JOIN `tabHoliday` h ON h.parent = hl.name AND h.parenttype = 'Holiday List'
					WHERE h.holiday_date = %s 
					AND hl.name IN ({})
				""".format(','.join(['%s'] * len(holiday_lists))), 
				[self.yesterday] + list(holiday_lists), as_dict=False)
				
				self._holiday_lists = {row[0] for row in result}
		
		return self._holiday_lists

	def send_notification_mail(self, recipient, employee_name):
		try:
			msg = frappe.render_template(
				'one_fm/templates/emails/employee_daily_action_check.html', 
				context={"employee_name": employee_name, "yesterday": self.yesterday}
			)

			sender = frappe.get_value("Email Account", 
									filters={"default_outgoing": 1}, 
									fieldname="email_id") or None
			
			sendemail(
				sender=sender, 
				recipients=[recipient],
				content=msg, 
				subject="Employee Daily Action Check", 
				delayed=False, 
				is_scheduler_email=True,
			)
		except Exception as e:
			frappe.log_error(f"Failed to send notification to {recipient}: {str(e)}", 
							"Employee Daily Action Check Notification")

	def notify_employee(self):
		if not self.non_compliant_employees:
			return
		
		
		employee_schedules = self.shift_working_employee_schedule
		leave_attendance = self.leave_attendance
		holiday_status = self.yesterday_holiday_status
		
		for employee in self.non_compliant_employees:
			recipient = None
			should_notify = False
			

			if (
				(employee.shift_working and employee.name in employee_schedules)
				or
				(not employee.shift_working and employee.holiday_list not in holiday_status and employee.name not in leave_attendance)
			):
				recipient = get_approver_user(employee.name)
				should_notify = True
			
			if should_notify and recipient:
				self.send_notification_mail(
					recipient=recipient, 
					employee_name=employee.employee_name
				)



def run_employee_daily_action_check_notifications():
    notifier = NotifyReportsToOnAbsenceOfReport()
    notifier.notify_employee()

		