def get_quality_feedback_template_custom_fields():
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
				"fieldname": "custom_feedback_schedule",
				"fieldtype": "Link",
				"label": "Feedback Schedule",
				"options": "Feedback Schedule",
				"in_list_view": 1,
				"reqd": 1,
				"insert_after": "custom_column_break_8dfte"
			},
			{
				"fieldname": "custom_is_enabled",
				"fieldtype": "Check",
				"label": "Enabled",
				"insert_after": "custom_feedback_schedule"
			},
			{
				"fieldname": "custom_tab_break_damaged_attachments",
				"fieldtype": "Tab Break",
				"label": "Damaged Attachments",
				"read_only": 1,
				"print_hide": 1,
				"insert_after": "parameters"
			},
			{
				"fieldname": "custom_damaged_attachments_html",
				"fieldtype": "HTML",
				"label": "Damaged Attachments Grid",
				"print_hide": 1,
				"read_only": 1,
				"insert_after": "custom_tab_break_damaged_attachments"
			}
		]
	}
