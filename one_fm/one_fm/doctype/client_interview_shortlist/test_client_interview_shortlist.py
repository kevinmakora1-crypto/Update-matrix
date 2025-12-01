# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate

from one_fm.one_fm.doctype.client_interview_shortlist.test_client_interview_shortlist_fixtures import (
	create_client_interview_shortlist,
)


class TestClientInterviewShortlist(FrappeTestCase):
	def setUp(self):
		self.employee = frappe.get_doc(
			{
				"doctype": "Employee",
				"employee_name": "Test Employee",
				"company": "_Test Company",
				"date_of_joining": "2025-01-01",
				"department": "_Test Department",
			}
		).insert(ignore_if_duplicate=True)
		self.project = frappe.get_doc(
			{
				"doctype": "Project",
				"project_name": "Test Project",
			}
		).insert(ignore_if_duplicate=True)

	def tearDown(self):
		frappe.db.rollback()

	def test_create_employee_schedule_on_submit(self):
		shortlist = create_client_interview_shortlist(self.employee.name, self.project.name)
		shortlist.submit()

		schedule_exists = frappe.db.exists(
			"Employee Schedule",
			{
				"employee": self.employee.name,
				"date": shortlist.interview_date,
				"employee_availability": "Client Interview",
				"project": self.project.name,
			},
		)
		self.assertTrue(schedule_exists)

	def test_replace_existing_employee_schedule_on_submit(self):
		interview_date = getdate("2025-11-30")
		# Create an existing schedule
		existing_schedule = frappe.get_doc(
			{
				"doctype": "Employee Schedule",
				"employee": self.employee.name,
				"date": interview_date,
				"employee_availability": "Working",
			}
		).insert(ignore_permissions=True)

		shortlist = create_client_interview_shortlist(
			self.employee.name, self.project.name, interview_date=interview_date
		)
		shortlist.submit()

		# Check that the old schedule is deleted
		self.assertFalse(frappe.db.exists("Employee Schedule", existing_schedule.name))

		# Check that the new schedule is created
		new_schedule_exists = frappe.db.exists(
			"Employee Schedule",
			{
				"employee": self.employee.name,
				"date": interview_date,
				"employee_availability": "Client Interview",
				"project": self.project.name,
			},
		)
		self.assertTrue(new_schedule_exists)
