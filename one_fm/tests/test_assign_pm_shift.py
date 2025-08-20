import frappe
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
from frappe.utils import getdate, cstr, now, add_days

# Import the functions to be tested from the main application file
# Ensure this import path is correct for your project's structure
from one_fm.api.tasks import assign_pm_shift

class TestAssignPMShift(unittest.TestCase):

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
    def test_assign_pm_shift_with_roster(self, mock_create_shift_assignment, mock_end_previous_shifts, mock_fetch_non_shift, mock_render_template, mock_log_error, mock_get_value, mock_get_today_leaves, mock_get_user_default, mock_get_list, mock_get_doc, mock_sql):
        """
        Test that shift assignments are created when eligible employees exist.
        This test mocks all external dependencies to ensure the logic of assign_pm_shift is tested in isolation.
        """
        
        # Mocking external function returns
        # Mock for frappe.defaults.get_user_default
        mock_get_user_default.return_value = "Test Company"
        
        # Mock for one_fm.api.tasks.get_today_leaves
        mock_get_today_leaves.return_value = []
        
        # Mock for frappe.get_doc
        mock_get_doc.return_value.as_dict.return_value = {
            "name": "Standard|Morning|08:00:00-17:00:00|9 hours",
            "start_time": timedelta(hours=8),
            "end_time": timedelta(hours=17)
        }
        
        # Mock for frappe.db.get_list
        mock_get_list.return_value = [
            {"name": "Site A", "site_location": "Location A"}
        ]

        # Mock for one_fm.api.tasks.fetch_non_shift
        mock_fetch_non_shift.return_value = []
        
        # Mock frappe.db.sql for all its different calls
        mock_sql.side_effect = [
            # 1. SQL query for `tabEmployee Schedule` (roster)
            [{"employee": "EMP-001", "employee_name": "John Doe", "shift_type": "PM", "site": "Site A", "project": "Project A", "department": "Operations", "shift": "PM Shift", "operations_role": "PM", "post_abbrv": "PM", "roster_type": "Basic"}],
            
            # 2. SQL query for `tabShift Type`
            [{"name": "PM Shift", "shift_type": "PM", "start_time": timedelta(hours=13), "end_time": timedelta(hours=22)}],
            
            # 3. SQL query for `tabEmployee` with `status='Vacation'`
            [],
            
            # 4. SQL query for `tabShift Assignment`
            [],
            
            # 5. SQL query for `tabShift Request`
            [],
            
            # 6. SQL query for `tabOperations Site`
            [{"name": "Site A", "site_location": "Location A"}]
        ]
        
        # Call the function being tested
        assign_pm_shift()
        
        # Assertions
        mock_end_previous_shifts.assert_called_with("PM")
        mock_create_shift_assignment.assert_called()
        mock_log_error.assert_not_called()

        # checking the arguments passed to create_shift_assignment
        self.assertTrue(mock_create_shift_assignment.called)
        self.assertEqual(mock_create_shift_assignment.call_args[0][0][0]['employee'], 'EMP-001')