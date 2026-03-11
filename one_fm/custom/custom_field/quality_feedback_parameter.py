def get_quality_feedback_parameter_custom_fields():
	return {
		"Quality Feedback Parameter": [
			{
				"fieldname": "custom_rating_scale_name",
				"fieldtype": "Link",
				"label": "Rating Scale",
				"options": "Rating Scale",
				"insert_after": "rating"
			},
			{
				"fieldname": "custom_rating_option",
				"fieldtype": "Data",
				"label": "Rating Option",
				"read_only": 1,
				"insert_after": "custom_rating_scale_name",
			},
			{
				"fieldname": "custom_rating_score",
				"fieldtype": "Int",
				"label": "Rating Score",
				"read_only": 1,
				"description": "This field stores the quantitative value of the selected Rating Option and Rating Scale.",
				"insert_after": "custom_rating_option",
			}
		]
	}
