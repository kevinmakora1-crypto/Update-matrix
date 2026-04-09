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
			"goal_description": "Test goal",
			"type": "Incremental Changes",
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


class TestSingleActiveLogValidation(FrappeTestCase):
	"""Ensure only one active (non-Completed) Pathfinder Log per process."""

	PROCESS_A = "_Test Process Single Active A"
	PROCESS_B = "_Test Process Single Active B"

	def setUp(self):
		for proc in (self.PROCESS_A, self.PROCESS_B):
			if not frappe.db.exists("Process", proc):
				frappe.get_doc({
					"doctype": "Process",
					"process_name": proc,
					"description": "Test process for single-active validation",
					"process_owner": "Administrator",
					"business_analyst": "Administrator",
				}).insert(ignore_permissions=True)

	def tearDown(self):
		for proc in (self.PROCESS_A, self.PROCESS_B):
			frappe.db.delete("Pathfinder Log", {"process_name": proc})
		frappe.db.commit()

	def _create_log(self, process_name, workflow_state="Draft"):
		doc = frappe.get_doc({
			"doctype": "Pathfinder Log",
			"process_name": process_name,
			"goal_description": "Test goal",
			"type": "Incremental Changes",
		})
		doc.insert(ignore_permissions=True)
		if workflow_state != "Draft":
			frappe.db.set_value(
				"Pathfinder Log", doc.name,
				"workflow_state", workflow_state,
				update_modified=True,
			)
			frappe.db.commit()
		return doc.name

	def test_first_log_succeeds(self):
		"""Creating the first non-Completed log for a process should succeed."""
		name = self._create_log(self.PROCESS_A)
		self.assertTrue(frappe.db.exists("Pathfinder Log", name))

	def test_second_active_log_blocked(self):
		"""A second non-Completed log for the same process should be blocked."""
		self._create_log(self.PROCESS_A, "In Development")
		with self.assertRaises(frappe.ValidationError) as ctx:
			self._create_log(self.PROCESS_A)
		self.assertIn("Only 1 active Pathfinder Log is allowed", str(ctx.exception))

	def test_allowed_after_completion(self):
		"""After the first log is Completed, a new one should be allowed."""
		self._create_log(self.PROCESS_A, "Completed")
		name = self._create_log(self.PROCESS_A)
		self.assertTrue(frappe.db.exists("Pathfinder Log", name))

	def test_resave_existing_active_log(self):
		"""Re-saving an already active log should not block itself."""
		name = self._create_log(self.PROCESS_A, "In Development")
		doc = frappe.get_doc("Pathfinder Log", name)
		doc.save(ignore_permissions=True)  # should not raise

	def test_different_processes_allowed(self):
		"""Different processes can each have their own active log."""
		self._create_log(self.PROCESS_A)
		name_b = self._create_log(self.PROCESS_B)
		self.assertTrue(frappe.db.exists("Pathfinder Log", name_b))
