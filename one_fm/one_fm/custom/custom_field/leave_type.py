def get_leave_type_custom_fields():
    """Return a dictionary of custom fields for the Leave Type document."""
    return {
        "Leave Type": [
			{
				"fieldname": "custom_update_employee_status_to_vacation",
				"fieldtype": "Check",
				"label": "Update Employee Status to Vacation",
				"insert_after": "custom_is_maternity",
				"description": 'If checked, Employee status will be updated to "Vacation" on "Leave Start Date" and reverted to "Active" on "Resumption Date".',
				"in_list_view": 1,
			},
		]
    }