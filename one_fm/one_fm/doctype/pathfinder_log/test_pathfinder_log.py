# Copyright (c) 2026, ONE FM and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPathfinderLog(FrappeTestCase):
	"""Unit tests for the Pathfinder Log editability API."""

	PROCESS_NAME = "_Test Process Editability"

	def setUp(self):
		"""Create a test Process record once per test."""
		if not frappe.db.exists("Process", self.PROCESS_NAME):
			frappe.get_doc({
				"doctype": "Process",
				"process_name": self.PROCESS_NAME,
				"description": "Test process for pathfinder editability checks",
				"process_owner": "Administrator",
				"business_analyst": "Administrator",
			}).insert(ignore_permissions=True)

	def tearDown(self):
		"""Clean up Pathfinder Logs created during tests."""
		frappe.db.delete(
			"Pathfinder Log",
			{"process_name": self.PROCESS_NAME},
		)
		frappe.db.commit()

	def _create_log(self, workflow_state="Draft"):
		"""Helper to create a Pathfinder Log with a given workflow_state."""
		doc = frappe.get_doc({
			"doctype": "Pathfinder Log",
			"process_name": self.PROCESS_NAME,
		})
		doc.insert(ignore_permissions=True)
		# Force workflow_state outside normal transitions for test isolation
		frappe.db.set_value(
			"Pathfinder Log", doc.name,
			"workflow_state", workflow_state,
			update_modified=True,
		)
		frappe.db.commit()
		return doc.name

	# ── is_process_editable ────────────────────────────────────────

	def test_no_log_returns_not_editable(self):
		"""Process with no Pathfinder Log should not be editable."""
		from one_fm.one_fm.doctype.pathfinder_log.pathfinder_api import (
			is_process_editable,
		)

		result = is_process_editable(self.PROCESS_NAME)
		self.assertFalse(result["editable"])
		self.assertIsNone(result["pathfinder_log"])
		self.assertIsNone(result["workflow_state"])

	def test_active_log_returns_editable(self):
		"""Process with a non-Completed log should be editable."""
		from one_fm.one_fm.doctype.pathfinder_log.pathfinder_api import (
			is_process_editable,
		)

		log_name = self._create_log("In Development")

		result = is_process_editable(self.PROCESS_NAME)
		self.assertTrue(result["editable"])
		self.assertEqual(result["pathfinder_log"], log_name)
		self.assertEqual(result["workflow_state"], "In Development")

	def test_completed_log_returns_not_editable(self):
		"""Process where all logs are Completed should not be editable."""
		from one_fm.one_fm.doctype.pathfinder_log.pathfinder_api import (
			is_process_editable,
		)

		self._create_log("Completed")

		result = is_process_editable(self.PROCESS_NAME)
		self.assertFalse(result["editable"])

	def test_most_recent_active_log_selected(self):
		"""When multiple active logs exist, the most recent is returned."""
		from one_fm.one_fm.doctype.pathfinder_log.pathfinder_api import (
			is_process_editable,
		)

		self._create_log("Draft")
		import time
		time.sleep(0.1)  # ensure modified timestamp differs
		newer_log = self._create_log("In Development")

		result = is_process_editable(self.PROCESS_NAME)
		self.assertTrue(result["editable"])
		self.assertEqual(result["pathfinder_log"], newer_log)
		self.assertEqual(result["workflow_state"], "In Development")

	def test_mixed_completed_and_active(self):
		"""If one log is Completed and another is active, process is editable."""
		from one_fm.one_fm.doctype.pathfinder_log.pathfinder_api import (
			is_process_editable,
		)

		self._create_log("Completed")
		active_log = self._create_log("In Staging")

		result = is_process_editable(self.PROCESS_NAME)
		self.assertTrue(result["editable"])
		self.assertEqual(result["pathfinder_log"], active_log)

	# ── bulk_check_process_editable ────────────────────────────────

	def test_bulk_check_maps_correctly(self):
		"""Bulk API should return per-process editability."""
		from one_fm.one_fm.doctype.pathfinder_log.pathfinder_api import (
			bulk_check_process_editable,
		)
		import json

		self._create_log("In Development")

		result = bulk_check_process_editable(
			json.dumps([self.PROCESS_NAME, "Nonexistent Process"])
		)

		self.assertIn(self.PROCESS_NAME, result)
		self.assertTrue(result[self.PROCESS_NAME]["editable"])

		self.assertIn("Nonexistent Process", result)
		self.assertFalse(result["Nonexistent Process"]["editable"])

	def test_bulk_check_invalid_json_raises(self):
		"""Malformed JSON should raise a validation error, not a 500."""
		from one_fm.one_fm.doctype.pathfinder_log.pathfinder_api import (
			bulk_check_process_editable,
		)

		with self.assertRaises(frappe.ValidationError):
			bulk_check_process_editable("not valid json {{{")

	def test_empty_process_name_raises(self):
		"""Calling is_process_editable with empty name should raise."""
		from one_fm.one_fm.doctype.pathfinder_log.pathfinder_api import (
			is_process_editable,
		)

		with self.assertRaises(frappe.ValidationError):
			is_process_editable("")
