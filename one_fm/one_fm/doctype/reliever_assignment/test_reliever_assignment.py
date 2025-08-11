# -*- coding: utf-8 -*-
# Copyright (c) 2025, ONE-F-M and Contributors
# See license.txt
from __future__ import unicode_literals
import frappe
import unittest
from one_fm.utils import set_employee_status
from frappe.utils import nowdate, add_to_date, cstr, cint, getdate, get_link_to_form



class TestRelieverAssignment(unittest.TestCase):
    def create_gender(self):
        frappe.get_doc({
        "doctype": "Gender",
        "gender":"Female",
        "custom_maternity_required":0,
        }).insert(ignore_permissions=True)
        
        frappe.get_doc({
        "doctype": "Gender",
        "gender":"Male",
        "custom_maternity_required":0,
        }).insert(ignore_permissions=True)
        
        frappe.db.commit()
            
    def setUp(self):
        self.leave_start_date = frappe.utils.getdate()
        self.leave_end_date = frappe.utils.add_days(self.leave_start_date, 1)
        self.resumption_date = frappe.utils.add_days(self.leave_start_date, 2)
        
        
        # Create Company and Holiday List
        frappe.local.flags.ignore_chart_of_accounts = 1
        frappe.flags.in_test = 1
        self.holiday_list = frappe.get_doc({
            "doctype": "Holiday List",
            "holiday_list_name": "Test Holiday List",
            "from_date": "2025-01-01",
            "to_date": "2025-12-31",
            "holidays": [
                {"description": "New Year", "holiday_date": "2025-01-01"}
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
        
        
        self.create_gender()
        self.basic = frappe.get_doc({
            "doctype": "Salary Component",
            "salary_component_abbr":"B",
            "salary_component": "Basic",
            "type": "Earning",
            "company": self.company.name
        }).insert(ignore_permissions=True)
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
		
        # Create Contacts and Users
        self.user_contact1 = frappe.get_doc({
            "doctype": "Contact",
            "first_name": "Alice"})
        self.user_contact2 = frappe.get_doc({
            "doctype": "Contact",
            "first_name": "Bob"})
        self.user_contact3 = frappe.get_doc({
            "doctype": "Contact",
            "first_name": "Charlie"})
        
        self.user_contact1.insert(ignore_permissions=True)
        
        self.user_contact1.append('email_ids', {
            "email_id": "alice@example.com"})
        
        self.user_contact2.insert(ignore_permissions=True)
        self.user_contact2.append('email_ids', {
            "email_id": "bob@example.com",})
        
        self.user_contact3.insert(ignore_permissions=True)
        self.user_contact3.append('email_ids', {
            "email_id": "charlie@example.com"})
        
        self.user1 = frappe.get_doc({
            "doctype": "User",
            "email": "alice@example.com",
            "first_name": "Alice",
            "last_name": "Rambo",
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
            "one_fm_is_paid_annual_leave":0,
            "leave_type_name": "Annual Leave",
            "custom_update_employee_status_to_vacation": 1,
            "is_annual_leave": 1
        }).insert(ignore_permissions=True)

        # Create Leave Allocation
        self.leave_allocation = frappe.get_doc({
            "doctype": "Leave Allocation",
            "employee": self.employee1.name,
            "leave_type": self.leave_type.name,
            "from_date": add_to_date(getdate(),days=-10),
            "to_date": add_to_date(getdate(),years=1),
            "new_leaves_allocated": 30
        }).insert(ignore_permissions=True)
        self.leave_allocation.submit()
        
        frappe.db.set_value("HR and Payroll Additional Settings",None, "default_leave_application_operator", self.employee3.user_id)
        is_active_workflow = frappe.get_all("Workflow", filters={"is_active": 1, "document_type": "Leave Application"}, fields=["name"])
        if is_active_workflow:
            #Disable the workflow for Leave Application
            frappe.db.set_value("Workflow", is_active_workflow[0].name, "is_active", 0)
        # Create Leave Application
        self.leave_application = frappe.get_doc({
            "doctype": "Leave Application",
            "employee": self.employee1.name,
            "leave_type": self.leave_type.name,
            "from_date": self.leave_start_date,
            "to_date": self.leave_end_date,
            "resumption_date": self.resumption_date,
            "status": "Approved",
            "workflow_state": "Approved",
            "custom_reliever_": self.employee2.name
        }).insert(ignore_permissions=True)
        self.leave_application.submit()


    def test_set_employee_status(self):
        # Simulate set_employee_status
        set_employee_status()
        # Reload employee1 and check status
        self.employee1.reload()
        self.assertEqual(self.employee1.status, "Vacation")

        # Reload ToDo and ensure it was reassigned to reliever (employee2's user)
        self.todo.reload()
        self.assertEqual(
            self.todo.allocated_to,
            self.employee2.user_id,
            f"ToDo was not reassigned to reliever: expected {self.employee2.user_id}, got {self.todo.allocated_to}"
        )

    def cancel_assignments(self):
        #Cancel The salary structure assignment
        all_user_perms = frappe.get_all("User Permission", filters={"allow": "Employee"})
        for each in all_user_perms:
            user_doc = frappe.get_doc("User Permission", each.name)
            user_doc.delete()
        all_strucs = frappe.get_all("Salary Structure Assignment", filters={"docstatus": 1})
        for each in all_strucs:
            doc = frappe.get_doc("Salary Structure Assignment", each.name)
            doc.cancel()
            doc.delete()
        #Cancel the 
            
    def tearDown(self):
        # Clean up created records
        frappe.db.set_value("HR and Payroll Additional Settings",None, "default_leave_application_operator",None)
        self.cancel_assignments()
        for doc in [self.leave_application, self.leave_allocation, self.leave_type, self.salary_structure, self.basic, self.housing, self.employee1, self.employee2, self.employee3, self.department1, self.department2, self.holiday_list, self.company, self.todo]:
            try:
                if doc.docstatus == 1:
                    doc.cancel()
                doc.delete()
            except Exception:
                pass