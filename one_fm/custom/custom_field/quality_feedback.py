def get_quality_feedback_custom_fields():
	return {
		"Quality Feedback": [
			{
				"fieldname": "custom_feedback_schedule",
				"fieldtype": "Link",
				"label": "Feedback Schedule",
				"options": "Feedback Schedule",
				"reqd": 1,
				"read_only": 1,
				"insert_after": "template",
				"fetch_from": "template.custom_feedback_schedule"
			},
			{
				"fieldname": "custom_feedback_schedule_stage",
				"fieldtype": "Link",
				"label": "Feedback Schedule Stage",
				"options": "Feedback Schedule Item",
				"reqd": 1,
				"insert_after": "custom_feedback_schedule"
			},
			{
				"fieldname": "custom_item_type",
				"fieldtype": "Link",
				"label": "Item Type",
				"options": "Item Type",
				"read_only": 1,
				"insert_after": "custom_feedback_schedule_stage"
			},
			{
				"fieldname": "custom_version_no",
				"fieldtype": "Data",
				"label": "Version No",
				"translatable": 1,
				"read_only": 1,
				"insert_after": "custom_item_type",
				"fetch_from": "template.custom_version_no"
			},
			{
				"fieldname": "custom_issued_on",
				"fieldtype": "Date",
				"label": "Issued On",
				"read_only": 1,
				"description": "This field will display the date when the item type has been issued via Stock Entry, Asset Movement or Employee Uniform.",
				"insert_after": "custom_version_no"
			},
			{
				"fieldname": "custom_feedback_due_on",
				"fieldtype": "Date",
				"label": "Feedback Due On",
				"read_only": 1,
				"insert_after": "custom_issued_on"
			},
			{
				"fieldname": "custom_employee",
				"fieldtype": "Link",
				"label": "Employee",
				"options": "Employee",
				"insert_after": "document_name"
			},
			{
				"fieldname": "custom_employee_name",
				"fieldtype": "Data",
				"label": "Employee Name",
				"read_only": 1,
				"translatable": 1,
				"fetch_from": "custom_employee.employee_name",
				"insert_after": "custom_employee"
			},
			{
				"fieldname": "custom_operations_site",
				"fieldtype": "Link",
				"label": "Operations Site",
				"options": "Operations Site",
				"fetch_from": "custom_employee.site",
				"insert_after": "custom_employee_name"
			},
			{
				"fieldname": "custom_noticed_damage",
				"fieldtype": "Select",
				"label": "Noticed Damage?",
				"options": "\nYes\nNo",
				"translatable": 1,
				"insert_after": "parameters"
			},
			{
				"fieldname": "custom_damage_description",
				"fieldtype": "Small Text",
				"label": "Damage Description",
				"translatable": 1,
				"depends_on": "eval:doc.custom_noticed_damage == \"Yes\"",
				"insert_after": "custom_noticed_damage"
			},
			{
				"fieldname": "custom_damage_attachment",
				"fieldtype": "Attach Image",
				"label": "Damage Attachment",
				"depends_on": "eval:doc.custom_noticed_damage == \"Yes\"",
				"insert_after": "custom_damage_description"
			},
			{
				"fieldname": "custom_feedback",
				"fieldtype": "Small Text",
				"label": "Feedback",
				"translatable": 1,
				"insert_after": "custom_damage_attachment"
			},
			{
				"fieldname": "custom_quality_score_percentage",
				"fieldtype": "Float",
				"label": "Quality Score Percentage",
				"read_only": 1,
				"insert_after": "custom_feedback"
			}
		]
	}
