
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, nowdate

from one_fm.tests.utils import (
    get_test_employee, get_test_leave_type, create_test_leave_allocation,
    create_test_company, make_leave_application
)
from frappe.workflow.doctype.workflow_action.workflow_action import apply_workflow
from unittest.mock import patch

def create_attendance_check_record(details, date):
    """Helper function to create an Attendance Check record"""
    attendance_check = frappe.get_doc({
        "doctype": "Attendance Check",
        "employee": details.get("employee"),
        "attendance": details.get("attendance"),
        "date": date,
        "roster_type": details.get("roster_type", ""),
        "shift_assignment": details.get("shift_assignment", ""),
        "attendance_status": details.get("attendance_status", ""),
        "comment": details.get("attendance_comment", ""),
    })
    attendance_check.insert()
    return attendance_check

class TestLeaveApplicationOverride(FrappeTestCase):
    """
    Complete test suite for the approve_attendance_check method from Leave Application
    
    This method:
    1. Finds all draft Attendance Check records for the employee within the leave period
    2. Updates their attendance_status to 'On Leave'
    3. Applies workflow approval to each Attendance Check
    4. Handles errors gracefully and logs them
    """
    
    def setUp(self):
        """Set up test data before each test"""
        frappe.set_user("Administrator")
        create_test_company()
        self.employee = get_test_employee()

        # Clean up existing test data
        frappe.db.delete("Attendance Check", {"employee": self.employee.name})
        frappe.db.delete("Leave Application", {"employee": self.employee.name})
        frappe.db.delete("Leave Allocation", {"employee": self.employee.name})

        self.leave_type = get_test_leave_type()
        create_test_leave_allocation(
            employee=self.employee,
            leave_type=self.leave_type,
            from_date=add_days(nowdate(), -30),
            to_date=add_days(nowdate(), 30),
            new_leaves_allocated=10
        )
    
    def tearDown(self):
        """Clean up after each test"""
        frappe.db.rollback()
        frappe.set_user("Administrator")
    
    def _create_draft_attendance_check(self, date, attendance_status="Absent"):
        """Helper to create a draft attendance check"""
        att_check_filters = {
            "employee": self.employee.name,
            "attendance_status": attendance_status
        }
        return create_attendance_check_record(att_check_filters, date)

    @patch("frappe.sendmail")
    def test_approve_leave_application_attendance_checks_approval(self, mock_sendmail):
        """Test 1: suite for approve_attendance_check method"""
        mock_sendmail.return_value = None
        leave_date = add_days(nowdate(), 1)
        attendance_check = self._create_draft_attendance_check(leave_date)

        # Create approved leave application
        leave_application = make_leave_application(
            self.employee.name,
            leave_date,
            leave_date,
            self.leave_type.name
        )
        leave_application.save()

        self.apply_approve_workflow(leave_application)

        # Verify attendance check status updated to 'On Leave'
        attendance_check.reload()
        self.assertEqual(attendance_check.attendance_status, "On Leave")
        
        # Verify workflow applied (docstatus = 1)
        self.assertEqual(attendance_check.docstatus, 1)
        
        # Verify database committed
        db_check = frappe.db.get_value(
            "Attendance Check",
            attendance_check.name,
            ["attendance_status", "docstatus"],
            as_dict=True
        )
        self.assertEqual(db_check.attendance_status, "On Leave")
        self.assertEqual(db_check.docstatus, 1)
    
    @patch("frappe.sendmail")
    def test_approve_leave_application_multiple_attendance_checks_approval(self, mock_sendmail):
        """Test 2: Multi-day leave with multiple draft attendance checks"""
        mock_sendmail.return_value = None
        from_date = add_days(nowdate(), 1)
        to_date = add_days(nowdate(), 5)

        # Create attendance checks for all days in the range
        attendance_checks = []
        for i in range(5):
            date = add_days(from_date, i)
            att_check = self._create_draft_attendance_check(date)
            attendance_checks.append(att_check)

        # Create approved leave application
        leave_application = make_leave_application(
            self.employee.name,
            from_date,
            to_date,
            self.leave_type.name,
        )

        leave_application.save()

        self.apply_approve_workflow(leave_application)
        
        # Verify all attendance checks are updated
        for att_check in attendance_checks:
            att_check.reload()
            self.assertEqual(att_check.attendance_status, "On Leave")
            self.assertEqual(att_check.docstatus, 1)

    @patch("frappe.sendmail")
    def test_partial_attendance_checks_in_range(self, mock_sendmail):
        """Test 3: Some days have attendance checks, some don't"""
        mock_sendmail.return_value = None
        from_date = add_days(nowdate(), 1)
        to_date = add_days(nowdate(), 5)

        # Create attendance checks only for days 1, 2
        check_1 = self._create_draft_attendance_check(from_date)
        check_2 = self._create_draft_attendance_check(add_days(from_date, 1))

        # Create approved leave application
        leave_application = make_leave_application(
            self.employee.name,
            from_date,
            to_date,
            self.leave_type.name
        )
        leave_application.save()

        self.apply_approve_workflow(leave_application)
        
        # Verify only existing checks are updated
        check_1.reload()
        check_2.reload()
        self.assertEqual(check_1.attendance_status, "On Leave")
        self.assertEqual(check_2.attendance_status, "On Leave")

        # Verify only 2 checks exist
        total_checks = frappe.db.count("Attendance Check", {
            "employee": self.employee.name,
            "date": ["between", [from_date, to_date]]
        })
        self.assertEqual(total_checks, 2)

    def apply_approve_workflow(self, doc):
        """Helper to apply approve workflow steps"""
        apply_workflow(doc, "Submit for Review")
        apply_workflow(doc, "Approve")