# Copyright (c) 2025, omar jaber and Contributors
# See license.txt

from datetime import date

import frappe
from frappe.tests.utils import FrappeTestCase


class TestEmployeeWeeklyAction(FrappeTestCase):
    pass

	# def setUp(self):
	# 	super().setUp()

	# 	# Ensure company exists
	# 	if not frappe.db.exists("Company", "ONEFM"):
	# 		frappe.get_doc({
	# 			"doctype": "Company",
	# 			"company_name": "ONEFM",
	# 			"default_currency": "QAR"
	# 		}).insert()

	# 	# Ensure department exists
	# 	if not frappe.db.exists("Department", "Engineering - ONEFM"):
	# 		frappe.get_doc({
	# 			"doctype": "Department",
	# 			"department_name": "Engineering",
	# 			"department_code": "ENG",
	# 			"company": "ONEFM"
	# 		}).insert()

	# 	# Ensure manager user exists
	# 	if not frappe.db.exists("User", "manager@example.com"):
	# 		manager_user = frappe.get_doc({
	# 			"doctype": "User",
	# 			"email": "manager@example.com",
	# 			"username": "manager_test",
	# 			"first_name": "Manager",
	# 			"last_name": "Test",
	# 			"enabled": 1
	# 		})
	# 		manager_user.insert(ignore_permissions=True)

	# 	# Create manager employee
	# 	self.manager = frappe.get_doc({
	# 		"doctype": "Employee",
	# 		"first_name": "Manager",
	# 		"last_name": "Test",
	# 		"employee_name": "Manager Test",
	# 		"user_id": "manager@example.com",
	# 		"gender": "Male",
	# 		"date_of_birth": "1990-01-01",
	# 		"date_of_joining": "2020-01-01",
	# 		"department": "Engineering - ONEFM",
	# 		"company": "ONEFM",
	# 		"one_fm_basic_salary": 1000,
	# 		"one_fm_first_name_in_arabic": "مدير",
	# 		"one_fm_last_name_in_arabic": "اختبار",
	# 	}).insert()

	# 	# Ensure subordinate user exists
	# 	if not frappe.db.exists("User", "john@example.com"):
	# 		employee_user = frappe.get_doc({
	# 			"doctype": "User",
	# 			"email": "john@example.com",
	# 			"username": "john_doe",
	# 			"first_name": "John",
	# 			"last_name": "Doe",
	# 			"enabled": 1
	# 		})
	# 		employee_user.insert(ignore_permissions=True)

	# 	# Create subordinate employee
	# 	self.employee = frappe.get_doc({
	# 		"doctype": "Employee",
	# 		"first_name": "John",
	# 		"last_name": "Doe",
	# 		"employee_name": "John Doe",
	# 		"user_id": "john@example.com",
	# 		"reports_to": self.manager.name,
	# 		"gender": "Male",
	# 		"date_of_birth": "1995-05-05",
	# 		"date_of_joining": "2023-01-01",
	# 		"department": "Engineering - ONEFM",
	# 		"company": "ONEFM",
	# 		"one_fm_basic_salary": 800,
	# 		"one_fm_first_name_in_arabic": "جون",
	# 		"one_fm_last_name_in_arabic": "دو",
	# 	}).insert()

	# 	frappe.set_user("john@example.com")


	# def tearDown(self):
	# 	frappe.set_user("Administrator")
	# 	frappe.db.rollback()

	# def test_blocker_created_on_submit(self):
	# 	# Create Employee Weekly Action with a blocker
	# 	weekly_action = frappe.get_doc({
	# 		"doctype": "Employee Weekly Action",
	# 		"employee": self.employee.name,
	# 		"week": 18,
	# 		"year": 2025,
	# 		"blockers": [{
	# 			"priority": "High",
	# 			"problem": "Database lag on report generation"
	# 		}]
	# 	}).insert(ignore_permissions=True)

	# 	weekly_action.submit()

	# 	# Query for the created blocker
	# 	blocker = frappe.get_all("Blocker", filters={
	# 		"user": self.employee.user_id,
	# 		"assigned_to": self.manager.user_id,
	# 		"priority": "High",
	# 		"blocker_details": "Database lag on report generation",
	# 		"date": date.today()
	# 	})

	# 	self.assertEqual(len(blocker), 1, "Expected 1 blocker to be created, found {}".format(len(blocker)))
