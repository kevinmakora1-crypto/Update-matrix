def get_quality_feedback_template_custom_fields():
	"""Return a dictionary of custom fields for the Quality Feedback Template document."""
	return {
		"Quality Feedback Template": [
			{
				"fieldname": "custom_item_type",
				"fieldtype": "Link",
				"label": "Item Type",
				"options": "Item Type",
				"in_list_view": 1,
				"reqd": 1,
				"insert_after": "template"
			},
			{
				"fieldname": "custom_version_no",
				"fieldtype": "Data",
				"label": "Version No",
				"translatable": 1,
				"insert_after": "custom_item_type"
			},
			{
				"fieldname": "custom_column_break_8dfte",
				"fieldtype": "Column Break",
				"insert_after": "custom_version_no"
			},
			{
				"fieldname": "custom_rating_scale",
				"fieldtype": "Link",
				"label": "Rating Scale",
				"options": "Rating Scale",
				"in_list_view": 1,
				"reqd": 1,
				"insert_after": "custom_column_break_8dfte"
			},
			{
				"fieldname": "custom_feedback_schedule",
				"fieldtype": "Link",
				"label": "Feedback Schedule",
				"options": "Feedback Schedule",
				"in_list_view": 1,
				"reqd": 1,
				"insert_after": "custom_rating_scale"
			},
			{
				"fieldname": "custom_is_enabled",
				"fieldtype": "Check",
				"label": "Enabled",
				"insert_after": "custom_feedback_schedule"
			}
		]
	}
