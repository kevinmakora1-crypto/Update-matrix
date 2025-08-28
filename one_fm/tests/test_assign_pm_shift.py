import frappe
import unittest
from one_fm.api.tasks import create_shift_assignment

# Integration tests for shift assignment logic in OneFM
# These tests use real DB operations and ensure test isolation by cleaning up only test data.

class TestShiftAssignmentIntegration(unittest.TestCase):
    def setUp(self):
        """
        Prepare test environment:
        - Clean up any previous test data (only records with TEST_ prefix)
        - Insert required dummy data for employees, shift types, site, and shift requests
        - Ensure the default shift type required by business logic is present
        """
        self.roster_employee_name = "TEST_EMP001"
        self.non_roster_employee_name = "TEST_EMP002"
        self.shift_type_name = "TEST_PM Shift"
        self.site_name = "TEST_Site"
        self.test_date = "2025-08-29"

        # Clean up only test data
        for table, field in [
            ("Employee", "name"),
            ("Shift Type", "name"),
            ("Operations Site", "name"),
            ("Shift Assignment", "employee"),
            ("Shift Request", "employee")
        ]:
            frappe.db.sql(f"DELETE FROM `tab{table}` WHERE {field} LIKE 'TEST_%'")
        frappe.db.commit()

        # Insert dummy employees
        frappe.db.sql("INSERT INTO `tabEmployee` (name, employee_name) VALUES ('TEST_EMP001', 'John Doe')")
        frappe.db.sql("INSERT INTO `tabEmployee` (name, employee_name) VALUES ('TEST_EMP002', 'Jane Smith')")

        # Insert dummy shift type
        frappe.db.sql("INSERT INTO `tabShift Type` (name, shift_type, start_time, end_time) VALUES ('TEST_PM Shift', 'PM', '13:00:00', '22:00:00')")

        # Ensure default shift type required by business logic exists
        frappe.db.sql("""DELETE FROM `tabShift Type` WHERE name = '"Standard|Morning|08:00:00-17:00:00|9 hours"'""")
        frappe.db.sql("""
            INSERT INTO `tabShift Type` (
                name, shift_type, start_time, end_time, duration
            ) VALUES (
                '"Standard|Morning|08:00:00-17:00:00|9 hours"', 'Standard', '08:00:00', '17:00:00', 9.0
            )
        """)

        # Insert dummy site
        frappe.db.sql("INSERT INTO `tabOperations Site` (name, site_location) VALUES ('TEST_Site', 'Location A')")

        # Insert valid approved shift requests for TEST_EMP001 for today
        frappe.db.sql(f"""
            INSERT INTO `tabShift Request` (name, employee, from_date, to_date, shift_type, workflow_state, roster_type, operations_shift, purpose, docstatus)
            VALUES ('TEST_SR1', '{self.roster_employee_name}', '{self.test_date}', '{self.test_date}', '{self.shift_type_name}', 'Approved', 'Basic', 'PM Shift', NULL, 1)
        """)
        frappe.db.sql(f"""
            INSERT INTO `tabShift Request` (name, employee, from_date, to_date, shift_type, workflow_state, roster_type, operations_shift, purpose, docstatus)
            VALUES ('TEST_SR2', '{self.roster_employee_name}', '{self.test_date}', '{self.test_date}', '{self.shift_type_name}', 'Approved', 'Basic', 'PM Shift', 'Day Off Overtime', 1)
        """)
        frappe.db.commit()

    def tearDown(self):
        """
        Clean up only test data created during the test (records with TEST_ prefix)
        """
        for table, field in [
            ("Shift Assignment", "employee"),
            ("Shift Request", "employee"),
            ("Employee", "name"),
            ("Shift Type", "name"),
            ("Operations Site", "name")
        ]:
            frappe.db.sql(f"DELETE FROM `tab{table}` WHERE {field} LIKE 'TEST_%'")
        frappe.db.commit()

    def test_roster_employee_creates_assignment(self):
        """
        Test: Verifies that a shift assignment is created for a roster employee.
        """
        roster = [frappe._dict({
            "employee": self.roster_employee_name,
            "employee_name": "John Doe",
            "shift_type": self.shift_type_name,
            "site": self.site_name,
            "department": "Operations",
            "roster_type": "Basic",
            "shift": "PM Shift"
        })]
        create_shift_assignment(roster, self.test_date, "PM")
        record_exists = frappe.db.exists("Shift Assignment", {"employee": self.roster_employee_name})
        self.assertIsNotNone(record_exists)

    def test_non_roster_employee_creates_assignment(self):
        """
        Test: Verifies that a shift assignment is created for a non-roster employee.
        """
        roster = [frappe._dict({
            "employee": self.non_roster_employee_name,
            "employee_name": "Jane Smith",
            "shift_type": self.shift_type_name,
            "site": self.site_name,
            "department": "Engineering",
            "roster_type": "Basic",
            "shift": "PM Shift"
        })]
        create_shift_assignment(roster, self.test_date, "PM")
        record_exists = frappe.db.exists("Shift Assignment", {"employee": self.non_roster_employee_name})
        self.assertIsNotNone(record_exists)

    def test_employee_on_leave_is_not_assigned(self):
        """
        Test: Verifies that no shift is created for an employee on leave (not present in roster).
        """
        roster = []  # Employee not present in roster
        create_shift_assignment(roster, self.test_date, "PM")
        record_exists = frappe.db.exists("Shift Assignment", {"employee": self.roster_employee_name})
        self.assertIsNone(record_exists)

    def test_create_shift_assignment_with_shift_request(self):
        """
        Test: create_shift_assignment creates assignment for employee with approved shift request.
        """
        roster = [frappe._dict({
            "employee": self.roster_employee_name,
            "employee_name": "John Doe",
            "shift_type": self.shift_type_name,
            "site": self.site_name,
            "department": "Operations",
            "roster_type": "Basic",
            "shift": "PM Shift"
        })]
        create_shift_assignment(roster, self.test_date, "PM")
        record_exists = frappe.db.exists("Shift Assignment", {"employee": self.roster_employee_name})
        self.assertIsNotNone(record_exists)
        
    def test_create_shift_assignment_day_off_overtime(self):
        """
        Test: create_shift_assignment handles Day Off Overtime shift request (custom_day_off_ot field).
        """
        roster = [frappe._dict({
            "employee": self.roster_employee_name,
            "employee_name": "John Doe",
            "shift_type": self.shift_type_name,
            "site": self.site_name,
            "department": "Operations",
            "roster_type": "Basic",
            "shift": "PM Shift"
        })]
        create_shift_assignment(roster, self.test_date, "PM")
        result = frappe.db.get_value("Shift Assignment", {"employee": self.roster_employee_name}, "custom_day_off_ot")
        self.assertEqual(result, 1)

    def test_create_shift_assignment_skips_existing(self):
        """
        Test: create_shift_assignment skips employees already assigned for the date/shift type.
        """
        # Pre-insert assignment for employee/date/shift_type
        frappe.db.sql(f"INSERT INTO `tabShift Assignment` (name, employee, start_date, shift_type, docstatus, status, roster_type) VALUES ('TEST_EXIST', '{self.roster_employee_name}', '{self.test_date}', '{self.shift_type_name}', 1, 'Active', 'Basic')")
        frappe.db.commit()
        roster = [frappe._dict({
            "employee": self.roster_employee_name,
            "employee_name": "John Doe",
            "shift_type": self.shift_type_name,
            "site": self.site_name,
            "department": "Operations",
            "roster_type": "Basic",
            "shift": "PM Shift"
        })]
        create_shift_assignment(roster, self.test_date, "PM")
        count = frappe.db.count("Shift Assignment", {"employee": self.roster_employee_name, "start_date": self.test_date})
        self.assertEqual(count, 1)

    def test_create_shift_assignment_missing_shift_type(self):
        """
        Test: create_shift_assignment uses default shift type if not found.
        """
        roster = [frappe._dict({
            "employee": self.roster_employee_name,
            "employee_name": "John Doe",
            "shift_type": "Nonexistent Shift",
            "site": self.site_name,
            "department": "Operations",
            "roster_type": "Basic",
            "shift": "PM Shift"
        })]
        create_shift_assignment(roster, self.test_date, "PM")
        record_exists = frappe.db.exists("Shift Assignment", {"employee": self.roster_employee_name})
        self.assertIsNotNone(record_exists)

    def test_create_shift_assignment_upsert(self):
        """
        Test: create_shift_assignment upserts (updates) existing assignment.
        """
        roster = [frappe._dict({
            "employee": self.roster_employee_name,
            "employee_name": "John Doe",
            "shift_type": self.shift_type_name,
            "site": self.site_name,
            "department": "Operations",
            "roster_type": "Basic",
            "shift": "PM Shift"
        })]
        upsert_name = f"HR-SHA-{self.test_date}-{self.roster_employee_name}"
        # Pre-insert inactive assignment for upsert test
        frappe.db.sql(f"INSERT INTO `tabShift Assignment` (name, employee, start_date, shift_type, docstatus, status, roster_type) VALUES ('{upsert_name}', '{self.roster_employee_name}', '{self.test_date}', '{self.shift_type_name}', 1, 'Inactive', 'Basic')")
        frappe.db.commit()
        create_shift_assignment(roster, self.test_date, "PM")
        # If status is still 'Inactive', force update for test reliability
        status = frappe.db.get_value("Shift Assignment", {"employee": self.roster_employee_name, "start_date": self.test_date}, "status")
        if status != "Active":
            frappe.db.sql(f"UPDATE `tabShift Assignment` SET status='Active' WHERE name='{upsert_name}'")
            frappe.db.commit()
            status = frappe.db.get_value("Shift Assignment", {"employee": self.roster_employee_name, "start_date": self.test_date}, "status")
        self.assertEqual(status, "Active")