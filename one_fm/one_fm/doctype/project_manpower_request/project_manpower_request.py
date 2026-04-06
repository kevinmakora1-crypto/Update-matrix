# Copyright (c) 2026, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ProjectManpowerRequest(Document):
	def before_submit(self):
		if not self.erf:
			frappe.throw(
				_("Please select an ERF before submitting this Project Manpower Request.")
			)

		# Validate that the linked ERF matches the designation
		erf_designation = frappe.db.get_value("ERF", self.erf, "designation")
		if erf_designation != self.designation:
			frappe.throw(
				_("The selected ERF ({0}) has designation '{1}' which does not match this PMR's designation '{2}'.").format(
					self.erf, erf_designation, self.designation
				)
			)
