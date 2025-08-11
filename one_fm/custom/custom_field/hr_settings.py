def get_hr_settings_fields():
    """Return a dictionary of custom fields for the HR Settings document."""
    return {
         "HR Settings": [
			{
				"fieldname": "annual_leave_threshold",
				"fieldtype": "Int",
				"label": "Annual Leave Threshold",
				"insert_after": "auto_leave_encashment",
				"default": 60,
				"description": "The minimum number of annual leave days an employee must accumulate before a leave acknowledgment form is automatically generated."
			},
		]
    }

