
import frappe
from frappe.tests.utils import FrappeTestCase
from one_fm.one_fm.doctype.attendance_check.attendance_check import AttendanceCheck

class TestAttendanceCheckLogic(FrappeTestCase):
    def setUp(self):
        super().setUp()
        # Create a test employee if not exists
        if not frappe.db.exists("Employee", "TEST-EMP-001"):
            emp = frappe.get_doc({
                "doctype": "Employee",
                "employee_number": "TEST-EMP-001",
                "first_name": "Test",
                "last_name": "Employee",
                "gender": "Male",
                "date_of_birth": "1990-01-01",
                "date_of_joining": "2020-01-01",
                "company": "ONE FM",
                "status": "Active"
            })
            emp.insert(ignore_permissions=True)
            self.employee = emp.name
        else:
            self.employee = "TEST-EMP-001"

    def test_mark_attendance_updates_existing(self):
        # Create an Attendance record
        attendance = frappe.get_doc({
            "doctype": "Attendance",
            "employee": self.employee,
            "attendance_date": "2024-01-01",
            "status": "Absent",
            "company": "ONE FM",
            "roster_type": "Basic"
        })
        attendance.insert(ignore_permissions=True)
        attendance.submit()
        
        # Create an Attendance Check record
        ac = frappe.get_doc({
            "doctype": "Attendance Check",
            "employee": self.employee,
            "date": "2024-01-01",
            "attendance_status": "Present",
            "roster_type": "Basic",
            "justification": "Other",
            "other_reason": "Test",
            "workflow_state": "Pending Approval" # Valid non-approved workflow state
        })
        ac.insert(ignore_permissions=True)
        
        # Manually call mark_attendance
        ac.mark_attendance()
        
        # Verify Attendance record is updated
        updated_attendance = frappe.get_doc("Attendance", attendance.name)
        self.assertEqual(updated_attendance.status, "Present")
        self.assertEqual(updated_attendance.reference_docname, ac.name)
        self.assertEqual(updated_attendance.comment, "Updated from Attendance Check")

    def tearDown(self):
        frappe.db.rollback()
        super().tearDown()
