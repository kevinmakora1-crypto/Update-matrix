# Copyright (c) 2026, ONE FM and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today

from one_fm.operations.doctype.temporary_post.temporary_post import mark_temporary_posts_as_completed

class TestTemporaryPost(FrappeTestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		# Clean any leftover records
		frappe.db.delete("Temporary Post", {"post_name": ["like", "Test Post%"]})

	def tearDown(self):
		frappe.db.delete("Temporary Post", {"post_name": ["like", "Test Post%"]})
		frappe.db.rollback()

	def test_mark_temporary_posts_as_completed(self):
		operations_role = frappe.db.get_value("Operations Role", {})
		
		# Create a temporary post with end_date in the past
		past_post = frappe.get_doc({
			"doctype": "Temporary Post",
			"post_name": "Test Post Past",
			"post_template": operations_role,
			"start_date": add_days(today(), -10),
			"end_date": add_days(today(), -5),
			"status": "Active",
			"gender": "Both"
		}).insert(ignore_mandatory=True, ignore_permissions=True)

		# Create a temporary post with end_date in the future
		future_post = frappe.get_doc({
			"doctype": "Temporary Post",
			"post_name": "Test Post Future",
			"post_template": operations_role,
			"start_date": today(),
			"end_date": add_days(today(), 5),
			"status": "Active",
			"gender": "Both"
		}).insert(ignore_mandatory=True, ignore_permissions=True)

		# Run the scheduled task
		mark_temporary_posts_as_completed()

		# Assert past_post status is updated to Completed
		self.assertEqual(frappe.db.get_value("Temporary Post", past_post.name, "status"), "Completed")

		# Assert future_post status is still Active
		self.assertEqual(frappe.db.get_value("Temporary Post", future_post.name, "status"), "Active")
