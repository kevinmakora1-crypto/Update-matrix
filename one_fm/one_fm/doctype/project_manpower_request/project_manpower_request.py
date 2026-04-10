# Copyright (c) 2026, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ProjectManpowerRequest(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		
		# Only generate autoname on first creation
		if not self.name:
			# Base sequence
			base_id = make_autoname("PR.#####")
			
			# Append suffix based on 'reason' or Manpower Type
			if self.reason == "Overtime":
				self.name = f"{base_id}-OT"
			elif self.reason == "Sub Contractor":
				self.name = f"{base_id}-SB"
			else:
				self.name = base_id
		
		# Sync the visual ID field
		self.project_request_code = self.name

	def validate(self):
		# An exit strictly replaces exactly 1 employee
		if self.reason == "Exit":
			self.count = 1
			
		self.calculate_remaining_qty()
		self.check_status_lock()
		self.validate_completion()

	def check_status_lock(self):
		if not self.is_new():
			old_status = frappe.db.get_value("Project Manpower Request", self.name, "status")
			terminal_statuses = ["Withdrawal Resignation", "Cancelled", "Completed"]
			
			if old_status in terminal_statuses and self.status != old_status:
				frappe.throw(
					_("The status cannot be changed further because it has already reached a terminal state: {0}").format(old_status)
				)

	def before_submit(self):
		if not self.erf:
			frappe.throw(
				_("Please select an ERF before submitting this Project Manpower Request.")
			)

		erf_designation = frappe.db.get_value("ERF", self.erf, "designation")
		if erf_designation != self.designation:
			frappe.throw(
				_("The selected ERF ({0}) has designation '{1}' which does not match this PMR's designation '{2}'.").format(
					self.erf, erf_designation, self.designation
				)
			)

	def validate_completion(self):
		if self.status == "Completed":
			hired_count = len(self.get('fulfilled_by_employees', []))
			if hired_count != self.remaining_qty:
				frappe.throw(
					_("To mark this PMR as Completed, you must link exactly {0} Employee(s) in the Closure Details section to match the Remaining Qty (Currently linked: {1}).").format(
						self.remaining_qty, hired_count
					)
				)

	def on_submit(self):
		self.db_set("status", "Open")

	def on_update(self):
		self.update_erf_headcount()
		
	def before_update_after_submit(self):
		self.calculate_remaining_qty()

	def on_update_after_submit(self):
		# Explicitly commit the recalculated totals to the DB
		self.db_set("remaining_qty", self.remaining_qty, update_modified=False)
		self.db_set("number_to_hire", self.number_to_hire, update_modified=False)
		self.update_erf_headcount()

	def on_trash(self):
		self.revert_erf_headcount()

	def calculate_remaining_qty(self):
		count = self.count or 0
		fulfilled = (
			(self.cancelled_qty or 0) +
			(self.managed_by_ot_qty or 0) +
			(self.managed_by_subcontractor_qty or 0) +
			(self.internal_transfer_qty or 0) +
			(self.resignation_withdrawal_qty or 0)
		)
		self.remaining_qty = max(0, count - fulfilled)
		
		# Number to hire = Remaining Qty minus the actual employees linked in the child table
		hired_count = len(self.get('fulfilled_by_employees', []))
		self.number_to_hire = max(0, self.remaining_qty - hired_count)

	def update_erf_headcount(self):
		if not self.erf:
			return

		# PMR only contributes to the ERF requirement if it is currently being processed or is historically completed.
		# If it is Open, Cancelled, or Withdrawn, its contribution should be 0.
		active_statuses = ["In Process", "Completed", "Internal Fulfilled", "Fulfilled by OT", "Fulfilled by Sub-con", "Fulfilled by OT & Sub"]
		target_contribution = self.remaining_qty if self.status in active_statuses else 0

		current_contribution = self.qty_added_to_erf or 0
		delta = target_contribution - current_contribution

		if delta != 0:
			current_erf_req = frappe.db.get_value("ERF", self.erf, "number_of_candidates_required") or 0
			new_req = current_erf_req + delta
			frappe.db.set_value("ERF", self.erf, "number_of_candidates_required", new_req)
			self.db_set("qty_added_to_erf", target_contribution, update_modified=False)
			
			direction = "increased" if delta > 0 else "decreased"
			frappe.msgprint(_("ERF {0} requirement {1} by {2}. Current Total: {3}").format(
				frappe.bold(self.erf), direction, frappe.bold(abs(delta)), frappe.bold(new_req)), alert=True)

	def revert_erf_headcount(self):
		if self.erf and self.qty_added_to_erf:
			current_erf_req = frappe.db.get_value("ERF", self.erf, "number_of_candidates_required") or 0
			frappe.db.set_value("ERF", self.erf, "number_of_candidates_required", current_erf_req - self.qty_added_to_erf)
