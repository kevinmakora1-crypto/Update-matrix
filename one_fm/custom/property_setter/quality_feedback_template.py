def get_quality_feedback_template_properties():
	return [
		{
			"doctype": "Property Setter",
			"doctype_or_field": "DocField",
			"doc_type": "Quality Feedback Template",
			"field_name": "parameters",
			"property": "reqd",
			"value": "0"
		},
		{
			"doctype": "Property Setter",
			"doctype_or_field": "DocField",
			"doc_type": "Quality Feedback Template Parameter",
			"field_name": "parameter",
			"property": "label",
			"value": "Survey Question"
		}
	]
