# -*- coding: utf-8 -*-
# Copyright (c) 2025, ONE-F-M and Contributors
# See license.txt
from __future__ import unicode_literals
import frappe
import unittest
from one_fm.utils import set_employee_status



class TestRelieverAssignment(unittest.TestCase):
    def setUp(self):
        # Create Company and Holiday List
        
        self.holiday_list = frappe.get_doc({
            "doctype": "Holiday List",
            "holiday_list_name": "Test Holiday List",
            "from_date": "2025-01-01",
            "to_date": "2025-12-31",
            "holidays": [
                {"description": "New Year", "holiday_date": "2025-01-01"},
                {"description": "Republic Day", "holiday_date": "2025-01-26"}
            ]
        }).insert(ignore_permissions=True)
        self.company = frappe.get_doc({
            "doctype": "Company",
            "company_name": "Test Company",
            "abbr": "TC",
            "default_currency": "KWD",
            "country": "Kuwait",
            "default_holiday_list": "Test Holiday List"
        }).insert(ignore_permissions=True)
        # Create Departments
        self.department1 = frappe.get_doc({
            "doctype": "Department",
            "department_code":"RANDO1234",
            "department_name": "Accounts",
            "company": self.company.name
        }).insert(ignore_permissions=True)
        self.department2 = frappe.get_doc({
            "doctype": "Department",
            "department_name": "HR",
            "department_code":"IDOUEO1234",
            "company": self.company.name
        }).insert(ignore_permissions=True)
        self.basic = frappe.get_doc("Salary Component","Basic")
        #Because Basic is created by default, we can use it directly
  
        self.housing = frappe.get_doc({
            "doctype": "Salary Component",
            "salary_component_abbr":"H",
            "salary_component": "Housing",
            "type": "Earning",
            "company": self.company.name
        }).insert(ignore_permissions=True)

        # Create Salary Structure
        self.salary_structure = frappe.get_doc({
            "doctype": "Salary Structure",
            "name": "Test Salary Structure",
            "company": self.company.name,
            "is_active": "Yes",
            "earnings": [
                {"salary_component": self.basic.name, "amount": 100},
                {"salary_component": self.housing.name, "amount": 50}
            ]
        }).insert(ignore_permissions=True)
        self.salary_structure.submit()
        # Create Employees
        self.employee1 = frappe.get_doc({
            "doctype": "Employee",
            "first_name": "Alice",
            "one_fm_first_name_in_arabic": "أليس",
            "last_name": "Sample Last",
            "one_fm_last_name_in_arabic": "عينة",
            "company": self.company.name,
            "department": self.department1.name,
            "date_of_birth": "1990-01-01",
            "date_of_joining": "2020-01-01",
            "gender": "Female",
            "status": "Active",
            "naming_series": "HR-EMP-",
            "employment_type": "Full-time",
            "job_offer_salary_structure": "Test Salary Structure",
            "one_fm_basic_salary": 100
        }).insert(ignore_permissions=True)
        self.employee2 = frappe.get_doc({
            "doctype": "Employee",
            "first_name": "Bob",
            "one_fm_first_name_in_arabic": "بوب",
            "last_name": "Sample Last",
            "one_fm_last_name_in_arabic": "عينة",
            "company": self.company.name,
            "department": self.department2.name,
            "date_of_birth": "1991-01-01",
            "date_of_joining": "2020-01-01",
            "gender": "Male",
            "status": "Active",
            "naming_series": "HR-EMP-",
            "employment_type": "Full-time",
            "job_offer_salary_structure": "Test Salary Structure",
            "one_fm_basic_salary": 100
        }).insert(ignore_permissions=True)
        self.employee3 = frappe.get_doc({
            "doctype": "Employee",
            "first_name": "Charlie",
            "one_fm_first_name_in_arabic": "تشارلي",
            "last_name": "Sample Last",
            "one_fm_last_name_in_arabic": "عينة",
            "company": self.company.name,
            "department": self.department1.name,
            "date_of_birth": "1992-01-01",
            "date_of_joining": "2020-01-01",
            "gender": "Male",
            "status": "Active",
            "naming_series": "HR-EMP-",
            "employment_type": "Full-time",
            "job_offer_salary_structure": "Test Salary Structure",
            "one_fm_basic_salary": 100
        }).insert(ignore_permissions=True)
		
        # Create Salary Components
        
        # Create Salary Structure
        self.user1 = frappe.get_doc({
            "doctype": "User",
            "email": "alice@example.com",
            "first_name": "Alice",
            "enabled": 1
        }).insert(ignore_permissions=True)
        self.employee1.user_id = self.user1.name
        self.employee1.save(ignore_permissions=True)

        self.user2 = frappe.get_doc({
            "doctype": "User",
            "email": "bob@example.com",
            "first_name": "Bob",
            "enabled": 1
        }).insert(ignore_permissions=True)
        self.employee2.user_id = self.user2.name
        self.employee2.save(ignore_permissions=True)

        self.user3 = frappe.get_doc({
            "doctype": "User",
            "email": "charlie@example.com",
            "first_name": "Charlie",
            "enabled": 1
        }).insert(ignore_permissions=True)
        self.employee3.user_id = self.user3.name
        self.employee3.save(ignore_permissions=True)


        # Create a sample ToDo
        self.todo = frappe.get_doc({
            "doctype": "ToDo",
            "notify_allocated_to_via_email":0,
            "description": "Test ToDo for Reliever Assignment",
            "allocated_to": self.employee1.user_id if hasattr(self.employee1, 'user_id') else None
        }).insert(ignore_permissions=True)
        

        # Create Leave Types
        self.leave_type = frappe.get_doc({
            "doctype": "Leave Type",
            "leave_type_name": "Annual Leave",
            "custom_update_employee_status_to_vacation": 1,
            "is_annual_leave": 1
        }).insert(ignore_permissions=True)

        # Create Leave Allocation
        self.leave_allocation = frappe.get_doc({
            "doctype": "Leave Allocation",
            "employee": self.employee1.name,
            "leave_type": self.leave_type.name,
            "from_date": "2025-01-01",
            "to_date": "2025-12-31",
            "new_leaves_allocated": 30
        }).insert(ignore_permissions=True)
        self.leave_allocation.submit()

        # Create Leave Application
        self.leave_application = frappe.get_doc({
            "doctype": "Leave Application",
            "employee": self.employee1.name,
            "leave_type": self.leave_type.name,
            "from_date": "2025-07-01",
            "to_date": "2025-07-06",
            "status": "Approved",
            "workflow_state": "Approved",
            "custom_reliever_": self.employee2.name
        }).insert(ignore_permissions=True)

        # Create a sample ToDo
        self.todo = frappe.get_doc({
            "doctype": "ToDo",
            "description": "Test ToDo for Reliever Assignment",
            "allocated_to": self.employee1.user_id if hasattr(self.employee1, 'user_id') else None
        }).insert(ignore_permissions=True)

    def test_set_employee_status(self):
        # Simulate set_employee_status
        set_employee_status()
        # Reload employee1 and check status
        self.employee1.reload()
        self.assertEqual(self.employee1.status, "Vacation")

    def tearDown(self):
        # Clean up created records
        for doc in [self.leave_application, self.leave_allocation, self.leave_type, self.salary_structure, self.basic, self.housing, self.employee1, self.employee2, self.employee3, self.department1, self.department2, self.holiday_list, self.company, self.todo]:
            try:
                if doc.docstatus == 1:
                    doc.cancel()
                doc.delete()
            except Exception:
                pass
