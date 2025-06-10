def get_leave_type_custom_fields():
    """Return a dictionary of custom fields for the Leave Type document."""
    return {
        "Leave Type": [
			{
				"fieldname": "custom_update_employee_status_to_vacation",
				"fieldtype": "Check",
				"label": "Update Employee Status to Vacation",
				"insert_after": "custom_is_maternity",
				"description": "Determines whether the employee's document status should be automatically updated when the leave is active.",
				"in_list_view": 1,
			},
		]
    }