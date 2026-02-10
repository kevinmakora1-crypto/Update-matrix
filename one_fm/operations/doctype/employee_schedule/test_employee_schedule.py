
# -*- coding: utf-8 -*-
# Copyright (c) 2020, ONE FM and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate, add_days

class TestEmployeeSchedule(FrappeTestCase):
	def setUp(self):
		# Create test employee if not exists
		if not frappe.db.exists("Employee", "TEST-EMP-001"):
			doc = frappe.get_doc({
				"doctype": "Employee",
				"employee": "TEST-EMP-001",
				"employee_name": "Test Employee",
				"status": "Active",
				"gender": "Male",
				"date_of_birth": "1990-01-01",
				"date_of_joining": nowdate()
			})
			doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
		self.employee = "TEST-EMP-001"

	def test_block_change_from_ojt_to_working_with_linked_ojt(self):
		# Create Employee Schedule with OJT
		# We use a dummy name for OJT to avoid needing to create the record,
		# we'll use frappe.db.set_value to put it there if link validation fails on insert.

		schedule = frappe.get_doc({
			"doctype": "Employee Schedule",
			"employee": self.employee,
			"date": add_days(nowdate(), 20),
			"employee_availability": "On-the-job Training",
			"roster_type": "Basic"
		})
		schedule.insert(ignore_permissions=True)

		# Set the OJT field manually to bypass link validation if it exists
		frappe.db.set_value("Employee Schedule", schedule.name, "on_the_job_training", "OJT-MOCK-001")
		schedule.reload()

		# Try to change to Working
		schedule.employee_availability = "Working"

		expected_msg = "Cannot change availability to 'Working' while an OJT record is linked. To change to 'Working', please delete this schedule and create a new one through Roster."

		with self.assertRaises(frappe.ValidationError) as cm:
			schedule.save()

		self.assertIn(expected_msg, str(cm.exception))

	def test_allow_change_to_working_if_no_ojt_linked(self):
		# Create Employee Schedule without OJT
		schedule = frappe.get_doc({
			"doctype": "Employee Schedule",
			"employee": self.employee,
			"date": add_days(nowdate(), 21),
			"employee_availability": "On-the-job Training",
			"roster_type": "Basic"
		})
		schedule.insert(ignore_permissions=True)

		# Try to change to Working
		schedule.employee_availability = "Working"
		schedule.save() # Should not throw
		self.assertEqual(schedule.employee_availability, "Working")

	def test_allow_change_from_other_to_working_even_with_ojt_linked(self):
		# Create Employee Schedule with OJT but from Day Off
		schedule = frappe.get_doc({
			"doctype": "Employee Schedule",
			"employee": self.employee,
			"date": add_days(nowdate(), 22),
			"employee_availability": "Day Off",
			"roster_type": "Basic"
		})
		schedule.insert(ignore_permissions=True)

		# Set the OJT field manually
		frappe.db.set_value("Employee Schedule", schedule.name, "on_the_job_training", "OJT-MOCK-001")
		schedule.reload()

		# Try to change to Working
		schedule.employee_availability = "Working"
		schedule.save() # Should not throw as per requirement 1
		self.assertEqual(schedule.employee_availability, "Working")
