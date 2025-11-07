# Copyright (c) 2025, one_fm and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today
from one_fm.utils import get_approver_user

class MedicalAppointment(Document):
	def validate(self):
		if self.workflow_state == "Pending Confirmation" and self.date_and_time_confirmation:
			if self.date_and_time_confirmation > today():
				frappe.throw(
					_("You are not allowed to action medical appointment before the appointment date."),
					title=_("Appointment Date is in the future"),
				)
		self.set_approver()

	def set_approver(self):
		if not self.employee_supervisor and self.employee:
			self.employee_supervisor = get_approver_user(self.employee)
