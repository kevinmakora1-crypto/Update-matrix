import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, today, cint


class PenaltyAndInvestigation(Document):
	def validate(self):
		self.validate_duplicate_penalty()
		self.calculate_offence_count()

	def validate_duplicate_penalty(self):
		if not self.employee or not self.applied_penalty_code or not self.incident_date:
			return

		duplicate = frappe.db.exists(
			"Penalty And Investigation",
			{
				"employee": self.employee,
				"applied_penalty_code": self.applied_penalty_code,
				"incident_date": self.incident_date,
				"name": ["!=", self.name],
				"docstatus": ["!=", 2],
			},
		)

		if duplicate:
			frappe.throw(
				_("An active penalty investigation already exists for Employee {0} with Penalty Code {1} on {2}").format(
					self.employee, self.applied_penalty_code, self.incident_date
				)
			)

	def calculate_offence_count(self):
		if not self.employee or not self.applied_penalty_code or not self.incident_date:
			return

		# Get date 12 months ago from today
		twelve_months_ago = add_months(today(), -12)

		# Count previous occurrences for this employee and penalty code
		# We count records within the last 12 months, excluding the current record
		# We exclude cancelled records (docstatus 2)
		previous_count = frappe.db.count(
			"Penalty And Investigation",
			{
				"employee": self.employee,
				"applied_penalty_code": self.applied_penalty_code,
				"incident_date": [">=", twelve_months_ago],
				"name": ["!=", self.name],
				"docstatus": ["!=", 2],
			},
		)

		# The current offence count is the previous count plus this one
		self.offence_count = previous_count + 1

		# Set applied_level based on offence_count, capped at 5
		level = self.offence_count
		if level > 5:
			level = 5

		self.applied_level = str(level)


@frappe.whitelist()
def get_penalty_count():
	user = frappe.session.user
	count = frappe.db.count("Penalty And Investigation", {
		"employee_user": user,
		"docstatus": ["!=", 2]
	})

	return {
		"value": count,
		"fieldtype": "Int",
		"route": ["List", "Penalty And Investigation", "", {"docstatus": ["!=", 2]}]
	}


@frappe.whitelist()
def get_last_penalty_status():
	user = frappe.session.user
	latest_record = frappe.db.get_list(
		"Penalty And Investigation",
		filters={"employee_user": user},
		fields=["name", "workflow_state"],
		order_by="creation desc",
		limit=1,
	)

	if not latest_record:
		return {"value": _("None"), "fieldtype": "Data", "route": ["New", "Penalty And Investigation", ""]}

	record = latest_record[0]
	return {
		"value": f'{record.workflow_state}',
		"fieldtype": "Data",
		"route": ["Form", "Penalty And Investigation", record.name],
	}
