# Copyright (c) 2026, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint
from frappe.query_builder import DocType

class TemporaryDeployment(Document):
	def on_submit(self):
		"""Create Temporary Post records when workflow reaches Approved (doc_status = 1)."""
		if self.workflow_state == "Approved":
			self.create_temporary_posts()

	def create_temporary_posts(self):
		"""
		Iterate each row in `operations_post_requirement` and create
		`row.count` individual Temporary Post documents with numeric suffixes.

		Example:  post_name="Guard",  count=3  →  Guard-1, Guard-2, Guard-3
		"""
		created = []

		for row in self.operations_post_requirement:
			count = cint(row.count)
			if count <= 0:
				frappe.msgprint(
					frappe._("Row {0}: Count must be greater than 0. Skipped.").format(row.idx),
					alert=True,
				)
				continue

			for i in range(1, count + 1):
				post = frappe.get_doc({
					"doctype": "Temporary Post",
					"post_name": f"{row.post_name}-{i}",
					"post_template": row.operations_role,
					"start_date": self.start_date,
					"end_date": self.end_date,
					"gender": row.gender or "Both",
					"project": self.project,
					"site": self.operations_site,
					"status": "Active",
					"temporary_deployment": self.name,
				})
				post.insert(ignore_permissions=True)
				created.append(post.name)

		if created:
			frappe.msgprint(
				frappe._("{0} Temporary Post(s) created successfully.").format(len(created)),
				alert=True,
				indicator="green",
			)

	def on_cancel(self):
		TemporaryPost = DocType("Temporary Post")
		query = (frappe.qb.update(TemporaryPost)
			.set(TemporaryPost.status, "Completed")
			.where(TemporaryPost.temporary_deployment == self.name)
		)
		query.run()
