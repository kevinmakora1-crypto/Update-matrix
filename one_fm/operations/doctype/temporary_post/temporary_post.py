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
