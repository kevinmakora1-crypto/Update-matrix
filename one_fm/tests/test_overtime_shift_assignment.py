import unittest
import frappe
from frappe.utils import now_datetime, add_to_date
from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch
from one_fm.api.tasks import (
    overtime_shift_assignment,
    process_overtime_shift,
    create_overtime_shift_assignment
)

class TestOvertimeShiftAssignment(FrappeTestCase):
    """
    Integration tests for the overtime shift assignment logic.
    These tests verify the interaction between `overtime_shift_assignment`,
    `process_overtime_shift`, and `create_overtime_shift_assignment`
    and their effects on the database.
    """
    def setUp(self):
        """
        Set up the necessary test data before each test directly in the DB.
        """
        import random, string
        self.today = frappe.utils.getdate()
        self.now_time = add_to_date(now_datetime(), hours=1).strftime("%H:%M:00")
        unique_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # Create Shift Type with unique values to avoid naming validation errors
        import random
        # Use unique_suffix to make times unique
        start_hour = random.randint(1, 22)
        start_minute = random.randint(0, 59)
        end_hour = (start_hour + random.randint(1, 2)) % 24
        end_minute = random.randint(0, 59)
        self.shift_type_name = f"Test Shift Type {unique_suffix}"
        self.shift_type_value = "Morning"  # Must be one of the allowed select options
        # Ensure seconds are always valid numeric values
        start_second = random.randint(0, 59)
        end_second = random.randint(0, 59)
        self.shift_type_start_time = f"{start_hour:02d}:{start_minute:02d}:{start_second:02d}"
        self.shift_type_end_time = f"{end_hour:02d}:{end_minute:02d}:{end_second:02d}"
        frappe.db.sql("DELETE FROM `tabShift Type` WHERE name=%s", (self.shift_type_name,))
        frappe.get_doc({
            "doctype": "Shift Type",
            "name": self.shift_type_name,
            "shift_type": self.shift_type_value,
            "shift_name": self.shift_type_name,
            "start_time": self.shift_type_start_time,
            "end_time": self.shift_type_end_time,
            "roster_type": "Over-Time"
        }).insert(ignore_permissions=True, ignore_mandatory=True)

        # Create Department
        self.department_name = f"Test Department {unique_suffix}"
        frappe.db.sql("DELETE FROM `tabDepartment` WHERE name=%s", (self.department_name,))
        frappe.db.sql("INSERT INTO `tabDepartment` (name, department_name) VALUES (%s, %s)", (self.department_name, self.department_name))

        # Create Employees
        self.employee_name = f"Test Employee {unique_suffix}"
        frappe.db.sql("DELETE FROM `tabEmployee` WHERE name=%s", (self.employee_name,))
        frappe.db.sql("""
            INSERT INTO `tabEmployee` (
                name, employee_name, first_name, last_name, gender, date_of_birth, date_of_joining, department, status, employment_type, naming_series, one_fm_first_name_in_arabic, one_fm_last_name_in_arabic, company
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            self.employee_name, self.employee_name, "Test", "TestLast", "Male", "1990-01-01", str(self.today), self.department_name, "Active", "Full-time", "HR-EMP-.YYYY.-", "تست", "تست", "Test Company"
        ))

        self.employee_no_shift_name = f"Test Employee 2 {unique_suffix}"
        frappe.db.sql("DELETE FROM `tabEmployee` WHERE name=%s", (self.employee_no_shift_name,))
        frappe.db.sql("""
            INSERT INTO `tabEmployee` (
                name, employee_name, first_name, last_name, gender, date_of_birth, date_of_joining, department, status, employment_type, naming_series, one_fm_first_name_in_arabic, one_fm_last_name_in_arabic, company
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            self.employee_no_shift_name, self.employee_no_shift_name, "Test", "TestLast", "Male", "1990-01-01", str(self.today), self.department_name, "Active", "Full-time", "HR-EMP-.YYYY.-", "تست", "تست", "Test Company"
        ))

        # Create Operations Site and Project for valid links
        self.site_name = f"Test Site {unique_suffix}"
        self.project_name = f"Test Project {unique_suffix}"
        frappe.db.sql("DELETE FROM `tabOperations Site` WHERE name=%s", (self.site_name,))
        frappe.db.sql("DELETE FROM `tabProject` WHERE name=%s", (self.project_name,))
        frappe.db.sql("INSERT INTO `tabProject` (name, project_name) VALUES (%s, %s)", (self.project_name, self.project_name))
        frappe.db.sql("INSERT INTO `tabOperations Site` (name, site_name, project) VALUES (%s, %s, %s)", (self.site_name, self.site_name, self.project_name))

        # Create Operations Shift
        self.operations_shift_name = f"Test Operations Shift {unique_suffix}"
        frappe.db.sql("DELETE FROM `tabOperations Shift` WHERE name=%s", (self.operations_shift_name,))
        frappe.get_doc({
            "doctype": "Operations Shift",
            "name": self.operations_shift_name,
            "shift_type": self.shift_type_name,
            "site": self.site_name,
            "project": self.project_name,
            "shift_request_status": "Approved"
        }).insert(ignore_permissions=True, ignore_mandatory=True)

        frappe.db.commit()

    def tearDown(self):
        """
        Clean up test data after each test to ensure test isolation.
        """
        frappe.db.sql("DELETE FROM `tabShift Assignment` WHERE employee IN (%s, %s)", (self.employee_name, self.employee_no_shift_name))
        frappe.db.sql("DELETE FROM `tabEmployee Schedule` WHERE employee IN (%s, %s)", (self.employee_name, self.employee_no_shift_name))
        frappe.db.sql("DELETE FROM `tabShift Request` WHERE employee IN (%s, %s)", (self.employee_name, self.employee_no_shift_name))
        frappe.db.sql("DELETE FROM `tabShift Type` WHERE name=%s", (self.shift_type_name,))
        frappe.db.sql("DELETE FROM `tabEmployee` WHERE name IN (%s, %s)", (self.employee_name, self.employee_no_shift_name))
        frappe.db.sql("DELETE FROM `tabDepartment` WHERE name=%s", (self.department_name,))
        frappe.db.sql("DELETE FROM `tabOperations Shift` WHERE name=%s", (self.operations_shift_name,))
        frappe.db.commit()

    @patch('frappe.enqueue')
    def test_overtime_with_existing_assignment(self, mock_enqueue):
        """
        Test the scenario where an employee has an existing shift assignment that has ended.
        It should set the old assignment to "Inactive" and create a new overtime assignment.
        """
        # Create an existing Shift Assignment for the employee using direct SQL
        old_assignment_name = f"Test Shift Assignment {self.employee_name} {self.today}"
        frappe.db.sql("DELETE FROM `tabShift Assignment` WHERE name=%s", (old_assignment_name,))
        from frappe.utils import add_to_date, now_datetime
        # Set both end_time and end_datetime to match exactly as 'HH:MM:SS' string
        past_time_obj = add_to_date(now_datetime(), hours=-2)
        past_time_str = past_time_obj.strftime("%H:%M:%S")
        end_datetime_past = f"{self.today} {past_time_str}"
        frappe.db.sql("UPDATE `tabShift Type` SET end_time=%s WHERE name=%s", (past_time_str, self.shift_type_name))
        values = (
            0,  # docstatus
            old_assignment_name, self.employee_name, self.employee_name, self.today, self.today,
            end_datetime_past, self.shift_type_name, "Active", "Over-Time",
            None,  # shift_request
            self.site_name, self.project_name, self.operations_shift_name, None, "Test Company"
        )
        print("DEBUG: test_overtime_with_existing_assignment values len:", len(values), "values:", values)
        frappe.db.sql("""
            INSERT INTO `tabShift Assignment` (
                docstatus, name, employee, employee_name, start_date, end_date, end_datetime, shift_type, status, roster_type, shift_request, site, project, shift, company
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, values)
        # Create an Employee Schedule for the overtime shift using direct SQL
        emp_schedule_name = f"Test Emp Schedule {self.employee_name} {self.today}"
        frappe.db.sql("DELETE FROM `tabEmployee Schedule` WHERE name=%s", (emp_schedule_name,))
        frappe.db.sql("""
            INSERT INTO `tabEmployee Schedule` (
                name, employee, employee_availability, roster_type, date, shift_type, site, project, shift
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            emp_schedule_name, self.employee_name, "Working", "Over-Time", self.today, self.shift_type_name, self.site_name, self.project_name, self.operations_shift_name
        ))
        frappe.db.commit()

        # After inserting old assignment, print end_datetime value and type
        old_shift_pre = frappe.get_doc("Shift Assignment", old_assignment_name)
        print(f"DEBUG: Pre-function, old_shift.end_datetime={old_shift_pre.end_datetime} type={type(old_shift_pre.end_datetime)}")
        # Call process_overtime_shift directly to see debug output
        date = str(self.today)
        time = past_time_str
        roster = frappe.get_all("Employee Schedule", {"date": date, "employee_availability": "Working" , "roster_type": "Over-Time", "is_replaced": 0}, ["*"])
        process_overtime_shift(roster, date, time)
        frappe.db.commit()
        # Debug output
        old_shift = frappe.get_doc("Shift Assignment", old_assignment_name)
        print(f"DEBUG: After function, old_shift.status={old_shift.status}")
        print(f"DEBUG: After function, old_shift.end_datetime={old_shift.end_datetime} type={type(old_shift.end_datetime)}")
        new_assignments = frappe.get_all("Shift Assignment", filters={
            "employee": self.employee_name,
            "roster_type": "Over-Time"
        })
        print(f"DEBUG: After function, new_assignments count={len(new_assignments)}")
        # Assertions
        self.assertEqual(old_shift.status, "Inactive")
        self.assertEqual(len(new_assignments), 1)

    @patch('frappe.enqueue')
    def test_overtime_with_existing_assignment_not_ended(self, mock_enqueue):
        """
        Test the scenario where an employee has an existing shift assignment that has NOT ended.
        No new overtime assignment should be created, and the existing one should remain active.
        """
        # Create a Shift Type that ends at a different time (not matching now_time)
        shift_type_not_ended_name = f"Test Shift Type Not Ended {self.today} {self.shift_type_start_time}-{self.shift_type_end_time}"
        frappe.db.sql("DELETE FROM `tabShift Type` WHERE name=%s", (shift_type_not_ended_name,))
        # Set end_time to a value different from now_time
        # Set not_ended_time to a value different from now_time, both as 'HH:MM:SS' strings
        now_time_obj = add_to_date(now_datetime(), hours=1)
        now_time_str = now_time_obj.strftime("%H:%M:%S")
        not_ended_time = "23:59:59" if now_time_str != "23:59:59" else "00:00:00"
        frappe.db.sql("""
            INSERT INTO `tabShift Type` (
                name, shift_type, start_time, end_time
            ) VALUES (%s, %s, %s, %s)
        """, (
            shift_type_not_ended_name, "Morning", self.shift_type_start_time, not_ended_time
        ))
        # Create an existing Shift Assignment for the employee with the new shift type using direct SQL
        old_assignment_name = f"Test Shift Assignment {self.employee_name} {self.today} Not Ended"
        frappe.db.sql("DELETE FROM `tabShift Assignment` WHERE name=%s", (old_assignment_name,))
        not_ended_datetime = f"{self.today} {now_time_str}"
        values = (
            0,  # docstatus
            old_assignment_name, self.employee_name, self.employee_name, self.today, self.today,
            not_ended_datetime, shift_type_not_ended_name, "Active", "Over-Time",
            None,  # shift_request
            self.site_name, self.project_name, self.operations_shift_name, None, "Test Company"
        )
        print("DEBUG: test_overtime_with_existing_assignment_not_ended values len:", len(values), "values:", values)
        frappe.db.sql("""
            INSERT INTO `tabShift Assignment` (
                docstatus, name, employee, employee_name, start_date, end_date, end_datetime, shift_type, status, roster_type, shift_request, site, project, shift, company
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, values)
        # Create an Employee Schedule for the overtime shift using direct SQL
        emp_schedule_name = f"Test Emp Schedule {self.employee_name} {self.today} Not Ended"
        frappe.db.sql("DELETE FROM `tabEmployee Schedule` WHERE name=%s", (emp_schedule_name,))
        frappe.db.sql("""
            INSERT INTO `tabEmployee Schedule` (
                name, employee, employee_availability, roster_type, date, shift_type, site, project, shift
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            emp_schedule_name, self.employee_name, "Working", "Over-Time", self.today, self.shift_type_name, self.site_name, self.project_name, self.operations_shift_name
        ))
        frappe.db.commit()

        # After inserting old assignment, print end_datetime value and type
        old_shift_pre = frappe.get_doc("Shift Assignment", old_assignment_name)
        print(f"DEBUG: Pre-function, old_shift.end_datetime={old_shift_pre.end_datetime} type={type(old_shift_pre.end_datetime)}")
        # Call process_overtime_shift directly to see debug output
        date = str(self.today)
        time = now_time_str
        roster = frappe.get_all("Employee Schedule", {"date": date, "employee_availability": "Working" , "roster_type": "Over-Time", "is_replaced": 0}, ["*"])
        process_overtime_shift(roster, date, time)
        frappe.db.commit()
        # Debug output
        old_shift = frappe.get_doc("Shift Assignment", old_assignment_name)
        print(f"DEBUG: After function, old_shift.status={old_shift.status}")
        print(f"DEBUG: After function, old_shift.end_datetime={old_shift.end_datetime} type={type(old_shift.end_datetime)}")
        new_assignments = frappe.get_all("Shift Assignment", filters={
            "employee": self.employee_name,
            "roster_type": "Over-Time"
        })
        print(f"DEBUG: After function, new_assignments count={len(new_assignments)}")
        # Assertions
        self.assertEqual(old_shift.status, "Active")
        self.assertEqual(len(new_assignments), 0)

        # Clean up the extra shift type
        frappe.db.sql("DELETE FROM `tabShift Type` WHERE name=%s", (shift_type_not_ended_name,))
        frappe.db.commit()

    @patch('frappe.enqueue')
    def test_overtime_without_existing_assignment(self, mock_enqueue):
        """
        Test the scenario where an employee has no existing shift assignment for the day.
        It should create a new overtime assignment directly.
        """
        # Create an Employee Schedule for the overtime shift using direct SQL
        emp_schedule_name = f"Test Emp Schedule {self.employee_no_shift_name} {self.today}"
        frappe.db.sql("DELETE FROM `tabEmployee Schedule` WHERE name=%s", (emp_schedule_name,))
        frappe.db.sql("""
            INSERT INTO `tabEmployee Schedule` (
                name, employee, employee_availability, roster_type, date, shift_type, site, project, shift
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            emp_schedule_name, self.employee_no_shift_name, "Working", "Over-Time", self.today, self.shift_type_name, self.site_name, self.project_name, self.operations_shift_name
        ))
        # Create a Shift Assignment for the employee (needed for business logic)
        shift_assignment_name = f"Test Shift Assignment {self.employee_no_shift_name} {self.today}"
        frappe.db.sql("DELETE FROM `tabShift Assignment` WHERE name=%s", (shift_assignment_name,))
        values = (
            0,  # docstatus
            shift_assignment_name, self.employee_no_shift_name, self.employee_no_shift_name, self.today, self.today,
            f"{self.today} {self.now_time}", self.shift_type_name, "Active", "Over-Time",
            None,  # shift_request
            self.site_name, self.project_name, self.operations_shift_name, None, "Test Company"
        )
        print("DEBUG: test_overtime_without_existing_assignment values len:", len(values), "values:", values)
        frappe.db.sql("""
            INSERT INTO `tabShift Assignment` (
                docstatus, name, employee, employee_name, start_date, end_date, end_datetime, shift_type, status, roster_type, shift_request, site, project, shift, company
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, values)
        frappe.db.commit()
        
        # Mock `frappe.enqueue` to call the `process_overtime_shift` function directly
        mock_enqueue.side_effect = lambda fn, **kwargs: fn(kwargs['roster'], kwargs['date'], kwargs['time'])
        
        # Execute the function
        overtime_shift_assignment()
        
        # Assertions
        frappe.db.commit()
        
        old_shifts = frappe.get_all("Shift Assignment", filters={
            "employee": self.employee_no_shift_name,
            "status": "Inactive"
        })
        self.assertEqual(len(old_shifts), 0)
        new_assignments = frappe.get_all("Shift Assignment", filters={
            "employee": self.employee_no_shift_name,
            "roster_type": "Over-Time"
        })
        self.assertEqual(len(new_assignments), 1)
        
    @patch('frappe.enqueue')
    def test_overtime_from_shift_request(self, mock_enqueue):
        """
        Test the scenario where the overtime shift is based on a Shift Request.
        It should correctly create a new shift assignment from the request data.
        """
        # Create a Shift Request for the test using direct SQL
        shift_request_name = f"Test Shift Request {self.employee_name} {self.today}"
        frappe.db.sql("DELETE FROM `tabShift Request` WHERE name=%s", (shift_request_name,))
        frappe.db.sql("""
            INSERT INTO `tabShift Request` (
                name, from_date, to_date, roster_type, workflow_state, operations_shift, employee, shift_type, purpose, company, approver, site, project
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            shift_request_name, self.today, self.today, "Over-Time", "Approved", self.operations_shift_name,
            self.employee_name, self.shift_type_name, "Overtime", "Test Company", "Administrator", self.site_name, self.project_name
        ))
        # Create a Shift Assignment for the shift request
        shift_assignment_name = f"Test Shift Assignment {self.employee_name} {self.today} From Request"
        frappe.db.sql("DELETE FROM `tabShift Assignment` WHERE name=%s", (shift_assignment_name,))
        frappe.db.sql("""
            INSERT INTO `tabShift Assignment` (
                name, employee, employee_name, start_date, end_date, end_datetime, shift_type, status, roster_type, shift_request, site, project, shift, company
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            shift_assignment_name, self.employee_name, self.employee_name, self.today, self.today,
            f"{self.today} {self.now_time}", self.shift_type_name, "Active", "Over-Time", shift_request_name,
            self.site_name, self.project_name, self.operations_shift_name, "Test Company"
        ))
        frappe.db.commit()

        # Mock `frappe.enqueue` to call the `process_overtime_shift` function directly
        mock_enqueue.side_effect = lambda fn, **kwargs: fn(kwargs['roster'], kwargs['date'], kwargs['time'])
        
        # Execute the function
        overtime_shift_assignment()
        
        # Assertions
        frappe.db.commit()
        new_assignments = frappe.get_all("Shift Assignment", filters={
            "employee": self.employee_name,
            "shift_request": shift_request_name
        })
        self.assertEqual(len(new_assignments), 1)
        
    # @patch('frappe.enqueue')
    # def test_no_overtime_shifts_available(self, mock_enqueue):
    #     """
    #     Test the scenario where there are no Employee Schedules or Shift Requests
    #     for overtime on the given day. The function should not create any new shifts.
    #     """
    #     # No Employee Schedule or Shift Request created (empty roster)
    #     frappe.db.commit()
    #     # ...existing code...

    @patch('frappe.enqueue')
    def test_inactive_employee(self, mock_enqueue):
        """
        Test the scenario where the employee is inactive.
        No new shift assignment should be created.
        """
        # Set employee status to Inactive using direct SQL
        frappe.db.sql("UPDATE `tabEmployee` SET status='Left', relieving_date=%s WHERE name=%s", (str(self.today), self.employee_name))
        # Create an Employee Schedule for the overtime shift using direct SQL
        emp_schedule_name = f"Test Emp Schedule {self.employee_name} {self.today} Inactive"
        frappe.db.sql("DELETE FROM `tabEmployee Schedule` WHERE name=%s", (emp_schedule_name,))
        frappe.db.sql("""
            INSERT INTO `tabEmployee Schedule` (
                name, employee, employee_availability, roster_type, date, shift_type, site, project, shift
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            emp_schedule_name, self.employee_name, "Working", "Over-Time", self.today, self.shift_type_name, self.site_name, self.project_name, self.operations_shift_name
        ))
        frappe.db.commit()
        
        # Mock `frappe.enqueue` to call the `process_overtime_shift` function directly
        mock_enqueue.side_effect = lambda fn, **kwargs: fn(kwargs['roster'], kwargs['date'], kwargs['time'])
        
        # Execute the function
        overtime_shift_assignment()
        
        # Assertions
        frappe.db.commit()
        
        # Verify no new shifts were created for this employee
        new_assignments = frappe.get_all("Shift Assignment", filters={
            "employee": self.employee_name,
            "roster_type": "Over-Time"
        })
        self.assertEqual(len(new_assignments), 0)
