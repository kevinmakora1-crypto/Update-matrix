# Copyright (c) 2026, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TemporaryPost(Document):

	def before_insert(self):
		"""Ensure status is always Active when created automatically."""
		self.status = "Active"

	def validate(self):
		"""Prevent manual overriding of status to an invalid value."""
		if not self.status:
			self.status = "Active"

@frappe.whitelist()
def mark_temporary_posts_as_completed():
	"""Mark Temporary Posts as Completed if their end_date is less than today."""
	active_posts = frappe.get_all(
		"Temporary Post",
		filters={
			"status": "Active",
			"end_date": ["<", frappe.utils.today()]
		},
		pluck="name"
	)

	for post in active_posts:
		frappe.db.set_value("Temporary Post", post, "status", "Completed")
