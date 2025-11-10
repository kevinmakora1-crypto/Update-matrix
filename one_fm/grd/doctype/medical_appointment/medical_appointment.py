# Copyright (c) 2025, one_fm and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today
from one_fm.utils import get_approver_user

class MedicalAppointment(Document):
	def validate(self):
		self.validate_appointment_date()
		self.set_approver()

	def validate_appointment_date(self):
		if self.workflow_state == "Pending Confirmation" and self.date_and_time_confirmation:
			if self.date_and_time_confirmation > today():
				frappe.throw(
					_("You are not allowed to action medical appointment before the appointment date."),
					title=_("Appointment Date is in the future"),
				)

	def set_approver(self):
		if not self.employee_supervisor and self.employee:
			self.employee_supervisor = get_approver_user(self.employee)

	def on_update(self):
		self.notify_employee_supervisor_on_operations_site_rejection()

	def notify_employee_supervisor_on_operations_site_rejection(self):
		if self.workflow_state and self.has_value_changed("workflow_state"):
			if self.employee_supervisor and self.workflow_state == "Set Pick-up as Accommodation (Supervisor)":
				message = _(
					"This is to inform you that your request for site pickup for a medical appointment has been rejected. You can change the pickup location to Accommodation.<br/><br/>{0} {1}"
				).format(self.full_name, self.date_and_time_confirmation)

				notification_doc = {
					"doctype": "Notification Log",
					"subject": _("Medical Appointment Pickup Rejected"),
					"for_user": self.employee_supervisor,
					"document_type": self.doctype,
					"document_name": self.name,
					"email_content": message,
					"type": "Alert"
				}
				frappe.get_doc(notification_doc).insert(ignore_permissions=True)
