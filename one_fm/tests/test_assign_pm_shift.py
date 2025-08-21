
"""
Unit tests for assign_pm_shift in one_fm.api.tasks.
All external dependencies are mocked for isolated testing.
"""

import frappe
import unittest
from unittest.mock import patch
from datetime import timedelta

# Import the function to be tested
from one_fm.api.tasks import assign_pm_shift

class TestAssignPMShift(unittest.TestCase):
    """
    Test suite for assign_pm_shift function.
    Covers: normal roster assignment, non-roster employees, and leave scenarios.
    """

    @patch("frappe.db.sql")
    @patch("frappe.get_doc")
    @patch("frappe.db.get_list")
    @patch("frappe.defaults.get_user_default")
    @patch("one_fm.api.tasks.get_today_leaves")
    @patch("frappe.db.get_value")
    @patch("frappe.log_error")
    @patch("frappe.render_template")
    @patch("one_fm.api.tasks.fetch_non_shift")
    @patch("one_fm.api.tasks.end_previous_shifts")
    @patch("one_fm.api.tasks.create_shift_assignment")
    def test_assign_pm_shift_with_roster(
        self, mock_create_shift_assignment, mock_end_previous_shifts, mock_fetch_non_shift,
        mock_render_template, mock_log_error, mock_get_value, mock_get_today_leaves,
        mock_get_user_default, mock_get_list, mock_get_doc, mock_sql
    ):
        """
        Should create shift assignments when eligible employees exist in the PM roster.
        """
        # Setup mocks for a valid roster scenario
        mock_get_user_default.return_value = "Test Company"
        mock_get_today_leaves.return_value = []
        mock_get_doc.return_value.as_dict.return_value = {
            "name": "Standard|Morning|08:00:00-17:00:00|9 hours",
            "start_time": timedelta(hours=8),
            "end_time": timedelta(hours=17)
        }
        mock_get_list.side_effect = [
            [],  # Employees on vacation
            [],  # Existing shift assignments
            [],  # Shift requests
            [frappe._dict({"name": "Site A", "site_location": "Location A"})]  # Sites list
        ]
        mock_sql.side_effect = [
            [{"employee": "EMP-001", "employee_name": "John Doe", "shift_type": "PM", "site": "Site A", "project": "Project A", "department": "Operations", "shift": "PM Shift", "operations_role": "PM", "post_abbrv": "PM", "roster_type": "Basic"}],
            [{"name": "PM Shift", "shift_type": "PM", "start_time": timedelta(hours=13), "end_time": timedelta(hours=22)}]
        ]
        mock_fetch_non_shift.return_value = []

        # Execute function
        assign_pm_shift()

        # Assertions
        mock_end_previous_shifts.assert_called_with("PM")
        mock_create_shift_assignment.assert_called()
        mock_log_error.assert_not_called()
        self.assertEqual(mock_create_shift_assignment.call_args[0][0][0]['employee'], 'EMP-001')

    @patch("frappe.db.sql")
    @patch("frappe.get_doc")
    @patch("frappe.db.get_list")
    @patch("frappe.defaults.get_user_default")
    @patch("one_fm.api.tasks.get_today_leaves")
    @patch("frappe.db.get_value")
    @patch("frappe.log_error")
    @patch("frappe.render_template")
    @patch("one_fm.api.tasks.fetch_non_shift")
    @patch("one_fm.api.tasks.end_previous_shifts")
    @patch("one_fm.api.tasks.create_shift_assignment")
    def test_assign_pm_shift_with_non_roster_employees(
        self, mock_create_shift_assignment, mock_end_previous_shifts, mock_fetch_non_shift,
        mock_render_template, mock_log_error, mock_get_value, mock_get_today_leaves,
        mock_get_user_default, mock_get_list, mock_get_doc, mock_sql
    ):
        """
        Should create shift assignments for eligible employees not on the main roster.
        """
        # Setup mocks for non-roster employees
        mock_get_user_default.return_value = "Test Company"
        mock_get_today_leaves.return_value = []
        mock_get_doc.return_value.as_dict.return_value = {
            "name": "PM Shift", "start_time": timedelta(hours=13), "end_time": timedelta(hours=22)
        }
        mock_sql.side_effect = [
            [],  # Roster query returns empty
            [{"name": "PM Shift", "start_time": timedelta(hours=13), "end_time": timedelta(hours=22)}],
        ]
        mock_get_list.side_effect = [
            [frappe._dict({"name": "EMP-003"})],  # Employees on vacation
            [frappe._dict({"name": "Site A", "site_location": "Location A"})],  # Sites list
            [],  # Existing shift assignments
            [],  # Shift requests
        ]
        mock_fetch_non_shift.return_value = [
            {"employee": "EMP-002", "employee_name": "Jane Doe", "shift_type": "PM", "site": "Site A"}
        ]

        # Execute function
        assign_pm_shift()

        # Assertions
        mock_create_shift_assignment.assert_called()
        self.assertEqual(mock_create_shift_assignment.call_args[0][0][0]['employee'], 'EMP-002')

    @patch("frappe.db.sql")
    @patch("frappe.get_doc")
    @patch("frappe.db.get_list")
    @patch("frappe.defaults.get_user_default")
    @patch("one_fm.api.tasks.get_today_leaves")
    @patch("frappe.db.get_value")
    @patch("frappe.log_error")
    @patch("frappe.render_template")
    @patch("one_fm.api.tasks.fetch_non_shift")
    @patch("one_fm.api.tasks.end_previous_shifts")
    @patch("one_fm.api.tasks.create_shift_assignment")
    def test_assign_pm_shift_with_employee_on_leave(
        self, mock_create_shift_assignment, mock_end_previous_shifts, mock_fetch_non_shift,
        mock_render_template, mock_log_error, mock_get_value, mock_get_today_leaves,
        mock_get_user_default, mock_get_list, mock_get_doc, mock_sql
    ):
        """
        Should NOT create shift assignments for employees who are on leave.
        """
        # Setup mocks for leave scenario
        mock_get_user_default.return_value = "Test Company"
        mock_get_today_leaves.return_value = ["EMP-001"]
        mock_sql.side_effect = [
            [{"employee": "EMP-001", "employee_name": "John Doe", "shift_type": "PM", "site": "Site A"}],  # Roster query
            [{"name": "PM Shift", "start_time": timedelta(hours=13), "end_time": timedelta(hours=22)}],  # Shift Type query
            [], [], [], [], []
        ]
        mock_fetch_non_shift.return_value = []
        mock_get_list.return_value = []

        # Execute function
        assign_pm_shift()

        # Assertions
        mock_create_shift_assignment.assert_not_called()

if __name__ == "__main__":
    unittest.main()