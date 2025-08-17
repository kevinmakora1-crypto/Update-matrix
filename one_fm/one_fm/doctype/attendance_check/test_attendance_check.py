# Copyright (c) 2023, omar jaber and Contributors
# See license.txt

# import frappe
from frappe.tests.utils import FrappeTestCase, patch
import frappe
from one_fm.one_fm.doctype.attendance_check.attendance_check import (
	insert_attendance_check_records,
	create_attendance_check,
    get_absentees_on_date,
    get_attendance_not_marked_shift_employees,
    attendance_check_pending_approval_check,
    issue_penalty_to_the_assigned_approver,
    fetch_existing_todos,
    create_split_query,
    create_todos,
    notify_manager,
    assign_attendance_manager,
    schedule_attendance_check
	)


class TestAttendanceCheck(FrappeTestCase):

	def setUp(self):
		# Mock frappe.enqueue to avoid Redis errors during tests
		patcher = patch("frappe.enqueue", lambda *args, **kwargs: None)
		self.addCleanup(patcher.stop)
		patcher.start()

		# Create test Employee
		self.employee = frappe.get_doc({
            "doctype": "Employee",
            "employee_name": "Test Employee",
            "user_id": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "one_fm_first_name_in_arabic": "اختبار",
            "one_fm_last_name_in_arabic": "مستخدم",
            "gender": "Male",
            "date_of_birth": "1990-01-01",
            "date_of_joining": frappe.utils.today(),
            "department": "Operations - ONEFM",
            "one_fm_basic_salary": 1000
        }).insert(ignore_permissions=True)

		# Create test Shift Supervisor
		self.shift_supervisor = frappe.get_doc({
            "doctype": "Employee",
            "employee_name": "Shift Supervisor",
            "user_id": "shiftsupervisor@example.com",
            "first_name": "Shift",
            "last_name": "Supervisor",
            "one_fm_first_name_in_arabic": "اختبار",
            "one_fm_last_name_in_arabic": "مستخدم",
            "gender": "Male",
            "date_of_birth": "1992-01-01",
            "date_of_joining": frappe.utils.today(),
            "department": "Operations - ONEFM",
            "one_fm_basic_salary": 1200
        }).insert(ignore_permissions=True)

		# Check for existing Shift Type
		shift_type_name = "Morning"
		start_time = "06:00:00"
		end_time = "14:00:00"
		existing_shift_type = frappe.db.get_value(
			"Shift Type",
			{
				"shift_type": shift_type_name,
				"start_time": start_time,
				"end_time": end_time
			},
			"name"
		)
		if existing_shift_type:
			self.shift_type = frappe.get_doc("Shift Type", existing_shift_type)
		else:
			self.shift_type = frappe.get_doc({
				"doctype": "Shift Type",
				"shift_type": shift_type_name,
				"start_time": start_time,
				"end_time": end_time
			}).insert(ignore_permissions=True)

		# Create a Shift document for reference
		self.shift = frappe.get_doc({
			"doctype": "Operations Shift",
			"shift_name": "Test Shift",
			"start_time": "06:00:00",
			"end_time": "14:00:00",
			"working_hours": 8,
			"shift_number": 3,
			"service_type": "Security",
			"shift_type": self.shift_type.name
		}).insert(ignore_permissions=True)

		# Create Shift Assignment
		self.shift_assignment = frappe.get_doc({
			"doctype": "Shift Assignment",
			"employee": self.employee.name,
			"start_date": frappe.utils.today(),
			"roster_type": "Basic",
			"shift_type": self.shift_type.name,
			"shift": self.shift.name,
			"status": "Active",
			"docstatus": 1
		}).insert(ignore_permissions=True)

		# Create Attendance
		self.attendance = frappe.get_doc({
			"doctype": "Attendance",
			"employee": self.employee.name,
			"attendance_date": frappe.utils.today(),
			"status": "Absent",
			"roster_type": "Basic",
			"docstatus": 1,
			"is_unscheduled": 0,
			"shift_assignment": self.shift_assignment.name
		}).insert(ignore_permissions=True)

		# Create Attendance Request
		frappe.flags.ignore_supervisor_check = True
		self.attendance_request = frappe.get_doc({
			"doctype": "Attendance Request",
			"employee": self.employee.name,
			"from_date": frappe.utils.today(),
			"to_date": frappe.utils.today(),
			"explanation": "Anything",
			"docstatus": 1
		}).insert(ignore_permissions=True)
		frappe.flags.ignore_supervisor_check = False

		patcher_shift_permission = patch(
            "one_fm.operations.doctype.shift_permission.shift_permission.ShiftPermission.update_shift_assignment_checkin",
            lambda self: None
        )
		self.addCleanup(patcher_shift_permission.stop)
		patcher_shift_permission.start()

		# Create Shift Permission
		self.shift_permission = frappe.get_doc({
			"doctype": "Shift Permission",
			"employee": self.employee.name,
			"date": frappe.utils.today(),
			"roster_type": "Basic",
			"shift_type": self.shift_type.name,
			"shift_supervisor": self.shift_supervisor.name,
			"shift": self.shift.name,
			"assigned_shift": self.shift_assignment.name,
			"log_type": "IN",
			"reason": "Anything",
			"docstatus": 1,
			"workflow_state": "Draft"
		}).insert(ignore_permissions=True)

	def tearDown(self):
		# Bulk delete test records (bypasses hooks, safe for test data only)
		frappe.db.sql("DELETE FROM `tabAttendance Check` WHERE employee=%s", self.employee.name)
		frappe.db.sql("DELETE FROM `tabAttendance` WHERE name=%s", self.attendance.name)
		frappe.db.sql("DELETE FROM `tabShift Assignment` WHERE name=%s", self.shift_assignment.name)
		frappe.db.sql("DELETE FROM `tabAttendance Request` WHERE name=%s", self.attendance_request.name)
		frappe.db.sql("DELETE FROM `tabShift Permission` WHERE name=%s", self.shift_permission.name)
		frappe.db.sql("DELETE FROM `tabEmployee` WHERE name IN (%s, %s)", (self.employee.name, self.shift_supervisor.name))
		frappe.db.sql("DELETE FROM `tabShift Type` WHERE name=%s", self.shift_type.name)
		frappe.db.sql("DELETE FROM `tabOperations Shift` WHERE name=%s", self.shift.name)
		frappe.db.commit()

	def test_insert_attendance_check_record(self):
		details = [{
			"employee": self.employee.name,
			"attendance": self.attendance.name,
			"roster_type": "Basic",
			"shift_assignment": self.shift_assignment.name,
			"attendance_status": "Absent",
			"attendance_comment": "Absent reason"
		}]
		attendance_date = frappe.utils.today()
		insert_attendance_check_records(details, attendance_date)
		ac = frappe.get_last_doc("Attendance Check")
		self.assertEqual(ac.employee, self.employee.name)
		self.assertEqual(ac.attendance, self.attendance.name)
		self.assertEqual(ac.roster_type, "Basic")
		self.assertEqual(ac.shift_assignment, self.shift_assignment.name)
		self.assertEqual(ac.marked_attendance_status, "Absent")
		self.assertEqual(ac.comment, "Absent reason")
		self.assertEqual(ac.attendance_marked, 1)

	# def test_insert_duplicate_attendance_check_record(self):
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Absent"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	insert_attendance_check_records(details, attendance_date)
	# 	# Try to insert duplicate
	# 	with self.assertRaises(frappe.ValidationError):
	# 		insert_attendance_check_records(details, attendance_date)

	# def test_insert_attendance_check_with_attendance_by_timesheet(self):
	# 	frappe.db.set_value("Employee", self.employee.name, "attendance_by_timesheet", 1)
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Absent"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	insert_attendance_check_records(details, attendance_date)
	# 	ac = frappe.get_last_doc("Attendance Check")
	# 	self.assertTrue(ac.attendance_by_timesheet)

	# def test_insert_attendance_check_is_unscheduled(self):
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Absent"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	insert_attendance_check_records(details, attendance_date, is_unscheduled=True)
	# 	ac = frappe.get_last_doc("Attendance Check")
	# 	self.assertTrue(ac.is_unscheduled)

	# def test_insert_attendance_check_missing_optional_fields(self):
	# 	details = [{
	# 		"employee": self.employee.name
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	insert_attendance_check_records(details, attendance_date)
	# 	ac = frappe.get_last_doc("Attendance Check")
	# 	self.assertEqual(ac.roster_type, "Basic")
	# 	self.assertEqual(ac.attendance_marked, 0)
	# 	self.assertEqual(ac.comment, "")

	# def test_insert_multiple_attendance_check_records(self):
	# 	details = [
	# 		{
	# 			"employee": self.employee.name,
	# 			"attendance": self.attendance.name,
	# 			"roster_type": "Basic",
	# 			"shift_assignment": self.shift_assignment.name,
	# 			"attendance_status": "Absent"
	# 		},
	# 		{
	# 			"employee": self.employee.name,
	# 			"roster_type": "Basic"
	# 		}
	# 	]
	# 	attendance_date = frappe.utils.today()
	# 	insert_attendance_check_records(details, attendance_date)
	# 	ac_list = frappe.get_all("Attendance Check", filters={"employee": self.employee.name})
	# 	self.assertGreaterEqual(len(ac_list), 2)

	# def test_insert_attendance_check_error_logging(self):
	# 	# Simulate error by passing invalid employee
	# 	details = [{
	# 		"employee": "invalid_employee"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	# Should not raise, but should log error
	# 	insert_attendance_check_records(details, attendance_date)
	# 	# Check that no Attendance Check was created for invalid_employee
	# 	ac_list = frappe.get_all("Attendance Check", filters={"employee": "invalid_employee"})
	# 	self.assertEqual(len(ac_list), 0)

	# def test_insert_attendance_check_with_shift_permission(self):
	# 	# Employee with shift permission should have has_shift_permissions set
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Absent"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	insert_attendance_check_records(details, attendance_date)
	# 	ac = frappe.get_last_doc("Attendance Check")
	# 	self.assertEqual(ac.shift_permission, self.shift_permission.name)
	# 	self.assertEqual(ac.has_shift_permissions, 1)

	# def test_insert_attendance_check_with_attendance_request(self):
	# 	# Employee with attendance request should have attendance_request set
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Absent"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	insert_attendance_check_records(details, attendance_date)
	# 	ac = frappe.get_last_doc("Attendance Check")
	# 	self.assertEqual(ac.attendance_request, self.attendance_request.name)

	# def test_insert_attendance_check_with_checkin_records(self):
	# 	# Create Employee Checkin records
	# 	checkin_in = frappe.get_doc({
	# 		"doctype": "Employee Checkin",
	# 		"employee": self.employee.name,
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"log_type": "IN"
	# 	}).insert(ignore_permissions=True)
	# 	checkin_out = frappe.get_doc({
	# 		"doctype": "Employee Checkin",
	# 		"employee": self.employee.name,
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"log_type": "OUT"
	# 	}).insert(ignore_permissions=True)
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Absent"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	insert_attendance_check_records(details, attendance_date)
	# 	ac = frappe.get_last_doc("Attendance Check")
	# 	self.assertEqual(ac.checkin_record, checkin_in.name)
	# 	self.assertEqual(ac.checkout_record, checkin_out.name)
	# 	frappe.delete_doc("Employee Checkin", checkin_in.name)
	# 	frappe.delete_doc("Employee Checkin", checkin_out.name)

	# def test_insert_attendance_check_sets_approvers(self):
	# 	# Set reports_to, shift, site for employee
	# 	site = frappe.get_doc({
	# 		"doctype": "Operations Site",
	# 		"site_name": "Test Site",
	# 		"account_supervisor": "testuser@example.com"
	# 	}).insert(ignore_permissions=True)
	# 	frappe.db.set_value("Employee", self.employee.name, "reports_to", "testuser@example.com")
	# 	frappe.db.set_value("Employee", self.employee.name, "shift", self.shift_assignment.name)
	# 	frappe.db.set_value("Employee", self.employee.name, "site", site.name)
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Absent"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	insert_attendance_check_records(details, attendance_date)
	# 	ac = frappe.get_last_doc("Attendance Check")
	# 	self.assertEqual(ac.reports_to, "testuser@example.com")
	# 	self.assertEqual(ac.shift_supervisor, None) # get_shift_supervisor returns None in test
	# 	self.assertEqual(ac.site_supervisor, "testuser@example.com")
	# 	frappe.delete_doc("Operations Site", site.name)
            
	# def test_insert_attendance_check_duplicate_validation(self):
	# 	# Try to insert two AttendanceCheck records for same employee, date, roster_type
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Absent"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	insert_attendance_check_records(details, attendance_date)
	# 	with self.assertRaises(frappe.ValidationError):
	# 		insert_attendance_check_records(details, attendance_date)

	# def test_insert_attendance_check_links_shift_assignment_and_checkins(self):
	# 	# Insert valid Shift Assignment and Employee Checkin records
	# 	checkin_in = frappe.get_doc({
	# 		"doctype": "Employee Checkin",
	# 		"employee": self.employee.name,
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"log_type": "IN"
	# 	}).insert(ignore_permissions=True)
	# 	checkin_out = frappe.get_doc({
	# 		"doctype": "Employee Checkin",
	# 		"employee": self.employee.name,
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"log_type": "OUT"
	# 	}).insert(ignore_permissions=True)
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Absent"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	insert_attendance_check_records(details, attendance_date)
	# 	ac = frappe.get_last_doc("Attendance Check")
	# 	self.assertEqual(ac.shift_assignment, self.shift_assignment.name)
	# 	self.assertEqual(ac.checkin_record, checkin_in.name)
	# 	self.assertEqual(ac.checkout_record, checkin_out.name)
	# 	frappe.delete_doc("Employee Checkin", checkin_in.name)
	# 	frappe.delete_doc("Employee Checkin", checkin_out.name)

	# def test_insert_attendance_check_links_attendance_request_and_permission(self):
	# 	# Attendance Request and Shift Permission records for employee and date
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Absent"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	insert_attendance_check_records(details, attendance_date)
	# 	ac = frappe.get_last_doc("Attendance Check")
	# 	self.assertEqual(ac.attendance_request, self.attendance_request.name)
	# 	self.assertEqual(ac.shift_permission, self.shift_permission.name)
	# 	self.assertEqual(ac.has_shift_permissions, 1)

	# def test_insert_attendance_check_approver_assignment(self):
	# 	site = frappe.get_doc({
	# 		"doctype": "Operations Site",
	# 		"site_name": "Test Site",
	# 		"account_supervisor": "testuser@example.com"
	# 	}).insert(ignore_permissions=True)
	# 	frappe.db.set_value("Employee", self.employee.name, "reports_to", "testuser@example.com")
	# 	frappe.db.set_value("Employee", self.employee.name, "shift", self.shift_assignment.name)
	# 	frappe.db.set_value("Employee", self.employee.name, "site", site.name)
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Absent"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	insert_attendance_check_records(details, attendance_date)
	# 	ac = frappe.get_last_doc("Attendance Check")
	# 	self.assertEqual(ac.reports_to, "testuser@example.com")
	# 	self.assertEqual(ac.site_supervisor, "testuser@example.com")
	# 	frappe.delete_doc("Operations Site", site.name)

	# def test_insert_attendance_check_missing_justification_present(self):
	# 	# Missing justification for Present status
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Present"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	with self.assertRaises(Exception) as context:
	# 		insert_attendance_check_records(details, attendance_date)
	# 	self.assertIn("Please select Justification", str(context.exception))

	# def test_insert_attendance_check_other_justification_without_reason(self):
	# 	# "Other" justification without a reason
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Present",
	# 		"justification": "Other"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	with self.assertRaises(Exception) as context:
	# 		insert_attendance_check_records(details, attendance_date)
	# 	self.assertIn("Please write the other Reason", str(context.exception))

	# def test_insert_attendance_check_mobile_justification_without_brand_model(self):
	# 	# "Mobile isn't supporting the app" without brand/model
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Present",
	# 		"justification": "Mobile isn't supporting the app"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	with self.assertRaises(Exception) as context:
	# 		insert_attendance_check_records(details, attendance_date)
	# 	self.assertIn("Please select mobile brand", str(context.exception))

	# def test_insert_attendance_check_requires_screenshot(self):
	# 	# Justifications requiring screenshots
	# 	for justification in ["Invalid media content", "Out-of-site location", "User not assigned to shift"]:
	# 		details = [{
	# 			"employee": self.employee.name,
	# 			"attendance": self.attendance.name,
	# 			"roster_type": "Basic",
	# 			"shift_assignment": self.shift_assignment.name,
	# 			"attendance_status": "Present",
	# 			"justification": justification
	# 		}]
	# 		attendance_date = frappe.utils.today()
	# 		with self.assertRaises(Exception) as context:
	# 			insert_attendance_check_records(details, attendance_date)
	# 		self.assertIn("Please Attach ScreenShot", str(context.exception))

	# def test_insert_attendance_check_approved_by_admin_non_manager(self):
	# 	# "Approved by Administrator" by a non-manager
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Present",
	# 		"justification": "Approved by Administrator"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	with self.assertRaises(Exception) as context:
	# 		insert_attendance_check_records(details, attendance_date)
	# 	self.assertIn("Only the Attendance manager can select 'Approved by Administrator'", str(context.exception))

	# def test_insert_attendance_check_on_leave_triggers_leave_record_check(self):
	# 	# "On Leave" triggers leave record checks
	# 	leave_application = frappe.get_doc({
	# 		"doctype": "Leave Application",
	# 		"employee": self.employee.name,
	# 		"from_date": frappe.utils.today(),
	# 		"to_date": frappe.utils.today(),
	# 		"docstatus": 0
	# 	}).insert(ignore_permissions=True)
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "On Leave"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	with self.assertRaises(Exception) as context:
	# 		insert_attendance_check_records(details, attendance_date)
	# 	self.assertIn("Leave Application", str(context.exception))
	# 	frappe.delete_doc("Leave Application", leave_application.name)

	# def test_insert_attendance_check_day_off_triggers_shift_request_check(self):
	# 	# "Day Off" triggers shift request checks
	# 	shift_request = frappe.get_doc({
	# 		"doctype": "Shift Request",
	# 		"employee": self.employee.name,
	# 		"from_date": frappe.utils.today(),
	# 		"to_date": frappe.utils.today(),
	# 		"workflow_state": "Draft",
	# 		"approver": "testuser@example.com"
	# 	}).insert(ignore_permissions=True)
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Day Off"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	with self.assertRaises(Exception) as context:
	# 		insert_attendance_check_records(details, attendance_date)
	# 	self.assertIn("Shift Request", str(context.exception))
	# 	frappe.delete_doc("Shift Request", shift_request.name)

	# def test_insert_attendance_check_present_creates_attendance_record(self):
	# 	# "Present" creates or updates attendance records
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Present",
	# 		"justification": "Other",
	# 		"other_reason": "Test reason"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	insert_attendance_check_records(details, attendance_date)
	# 	ac = frappe.get_last_doc("Attendance Check")
	# 	ac.workflow_state = "Approved"
	# 	ac.save()
	# 	ac.on_submit()
	# 	attendance = frappe.get_last_doc("Attendance")
	# 	self.assertEqual(attendance.status, "Present")
	# 	self.assertEqual(attendance.working_hours, 8)
	# 	self.assertEqual(attendance.reference_doctype, "Attendance Check")
	# 	self.assertEqual(attendance.reference_docname, ac.name)

	# def test_insert_attendance_check_absent_creates_attendance_record(self):
	# 	# "Absent" creates or updates attendance records
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"roster_type": "Basic",
	# 		"attendance_status": "Absent"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	insert_attendance_check_records(details, attendance_date)
	# 	ac = frappe.get_last_doc("Attendance Check")
	# 	ac.workflow_state = "Approved"
	# 	ac.save()
	# 	ac.on_submit()
	# 	attendance = frappe.get_last_doc("Attendance")
	# 	self.assertEqual(attendance.status, "Absent")
	# 	self.assertEqual(attendance.working_hours, 0)
	# 	self.assertEqual(attendance.reference_doctype, "Attendance Check")
	# 	self.assertEqual(attendance.reference_docname, ac.name)

	# def test_insert_attendance_check_unscheduled_employee(self):
	# 	# Unscheduled employee handling
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"roster_type": "Basic"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	insert_attendance_check_records(details, attendance_date, is_unscheduled=True)
	# 	ac = frappe.get_last_doc("Attendance Check")
	# 	self.assertTrue(ac.is_unscheduled)

	# def test_insert_attendance_check_permission_check(self):
	# 	# Only attendance manager can approve certain justifications
	# 	details = [{
	# 		"employee": self.employee.name,
	# 		"attendance": self.attendance.name,
	# 		"roster_type": "Basic",
	# 		"shift_assignment": self.shift_assignment.name,
	# 		"attendance_status": "Present",
	# 		"justification": "Approved by Administrator"
	# 	}]
	# 	attendance_date = frappe.utils.today()
	# 	with self.assertRaises(Exception) as context:
	# 		insert_attendance_check_records(details, attendance_date)
	# 	self.assertIn("Only the Attendance manager can select 'Approved by Administrator'", str(context.exception))

	# def test_get_absentees_on_date(self):
	# 	absentees = get_absentees_on_date(frappe.utils.today())
	# 	self.assertTrue(any(a["employee"] == self.employee.name for a in absentees))

	# def test_get_attendance_not_marked_shift_employees(self):
    #     # Should return unscheduled employees (simulate by updating is_unscheduled)
	# 	frappe.db.set_value("Attendance", self.attendance.name, "is_unscheduled", 1)
	# 	result = get_attendance_not_marked_shift_employees(frappe.utils.today())
	# 	self.assertTrue(any(r["employee"] == self.employee.name for r in result))

	# @patch("one_fm.one_fm.doctype.attendance_check.attendance_check.production_domain", return_value=True)
	# @patch("one_fm.one_fm.doctype.attendance_check.attendance_check.insert_attendance_check_records")
	# def test_create_attendance_check(self, mock_insert, mock_domain):
	# 	create_attendance_check(frappe.utils.today())
	# 	self.assertTrue(mock_insert.called)

	# def test_fetch_existing_todos(self):
    #     # Create a ToDo for the employee
	# 	todo = frappe.get_doc({
    #         "doctype": "ToDo",
    #         "allocated_to": self.employee.user_id,
    #         "reference_type": "Attendance Check",
    #         "reference_name": "TestAttendanceCheck",
    #         "status": "Open"
    #     }).insert(ignore_permissions=True)
	# 	todos = fetch_existing_todos(self.employee.user_id)
	# 	self.assertIn("TestAttendanceCheck", todos)
	# 	frappe.delete_doc("ToDo", todo.name)
		
	# def test_create_split_query(self):
    #     # Simulate split query creation
	# 	todos = [{"name": "AC1"}, {"name": "AC2"}]
	# 	queries = create_split_query(todos, 1, "manager@example.com", frappe.utils.today(), frappe.utils.now())
	# 	self.assertEqual(len(queries), 2)
	# 	self.assertTrue("INSERT INTO `tabToDo`" in queries[0])

	# @patch("frappe.db.sql")
	# def test_create_todos(self, mock_sql):
	# 	todos = [type("obj", (object,), {"name": "AC1"})()]
	# 	create_todos("manager@example.com", todos)
	# 	self.assertTrue(mock_sql.called)

	# @patch("one_fm.processor.sendemail")
	# def test_notify_manager(self, mock_sendemail):
	# 	notify_manager("manager@example.com")
	# 	self.assertTrue(mock_sendemail.called)

	# @patch("one_fm.one_fm.doctype.attendance_check.attendance_check.fetch_attendance_manager_user", return_value="manager@example.com")
	# @patch("one_fm.one_fm.doctype.attendance_check.attendance_check.create_todos")
	# @patch("one_fm.one_fm.doctype.attendance_check.attendance_check.notify_manager")
	# def test_assign_attendance_manager(self, mock_notify, mock_create_todos, mock_fetch_manager):
	# 	pending = [type("obj", (object,), {"name": "AC1"})()]
	# 	assign_attendance_manager(pending)
	# 	self.assertTrue(mock_create_todos.called)
	# 	self.assertTrue(mock_notify.called)

	# @patch("frappe.enqueue")
	# def test_schedule_attendance_check(self, mock_enqueue):
	# 	schedule_attendance_check()
	# 	self.assertTrue(mock_enqueue.called)

	# @patch("frappe.db.get_single_value", return_value="PenaltyType")
	# @patch("frappe.get_doc")
	# def test_issue_penalty_to_the_assigned_approver(self, mock_get_doc, mock_get_single_value):
	# 	pending = [{"assign_to": '["manager@example.com"]', "name": "AC1"}]
	# 	issue_penalty_to_the_assigned_approver(pending)
	# 	self.assertTrue(mock_get_doc.called)

	# @patch("one_fm.one_fm.doctype.attendance_check.attendance_check.issue_penalty_to_the_assigned_approver")
	# @patch("one_fm.one_fm.doctype.attendance_check.attendance_check.assign_attendance_manager")
	# def test_attendance_check_pending_approval_check(self, mock_assign, mock_penalty):
	# 	with patch("one_fm.one_fm.doctype.attendance_check.attendance_check.get_pending_approval_attendance_check", return_value=[{"name": "AC1"}]):
	# 		attendance_check_pending_approval_check()
	# 		self.assertTrue(mock_penalty.called)
	# 		self.assertTrue(mock_assign.called)