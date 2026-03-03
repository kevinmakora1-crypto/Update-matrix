# Copyright (c) 2026, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import cstr, getdate, now
import pandas as pd

class TemporaryPost(Document):
	def before_insert(self):
		"""Ensure status is always Active when created automatically."""
		self.status = "Active"

	def validate(self):
		"""Prevent manual overriding of status to an invalid value."""
		if not self.status:
			self.status = "Active"

	def after_insert(self):
		self.create_post_schedule_for_temporary_post()

	def create_post_schedule_for_temporary_post(self):
		end_date = getdate(self.end_date)
		if end_date >= getdate():
			start_date = getdate(self.start_date)
			today = getdate()
			start_date = today if start_date < today else start_date
			exists_schedule_in_between = False
			if frappe.db.exists("Post Schedule", {"date": ['between', (start_date, end_date)], "temporary_post": self.name}):
				exists_schedule_in_between = True
			frappe.enqueue(generate_temporary_post_schedule, temporary_post=self, exists_schedule_in_between=exists_schedule_in_between, start_date=start_date, is_async=True, queue="long")
		else:
			frappe.msgprint(_("End date of the temporary post is less than today."))

def generate_temporary_post_schedule(temporary_post, exists_schedule_in_between, start_date):
	try:
		owner = frappe.session.user
		creation = now()
		query = """
			Insert Into
				`tabPost Schedule`
				(
					`name`, `temporary_post`, `operations_role`, `post_abbrv`, `shift`, `site`, `project`, `date`, `post_status`,
					`owner`, `modified_by`, `creation`, `modified`, `paid`
				)
			Values
		"""
		post_abbrv = frappe.db.get_value("Operations Role", temporary_post.post_template, ["post_abbrv"])
		#The previous series value from frappe is wrong in some cases

		for date in	pd.date_range(start=start_date, end=temporary_post.end_date):
			date_string = frappe.utils.get_date_str(date.date())
			doc_id_template = f"{temporary_post.name}_{date_string}"
			schedule_exists = False
			if exists_schedule_in_between:
				if frappe.db.exists("Post Schedule", {"date": cstr(date.date()),'operations_role': temporary_post.post_template, "temporary_post": temporary_post.name}):
					schedule_exists = True
			if not schedule_exists:
				query += f"""
					(
						"{doc_id_template}", "{temporary_post.name}", "{temporary_post.post_template}", "{post_abbrv}",
						"{temporary_post.site_shift}", "{temporary_post.site}", "{temporary_post.project}",
						'{cstr(date.date())}', 'Planned', "{owner}", "{owner}", "{creation}", "{creation}", '0'
					),"""

		frappe.db.sql(query[:-1], values=[], as_dict=1)
		frappe.db.commit()
		frappe.msgprint(_("Post is scheduled as Planned."))
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(message=str(e), title='Post Schedule from Temporary Post')
		frappe.msgprint(_("Error log is added."), alert=True, indicator='orange')
		temporary_post.reload()

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
