def get_quality_feedback_parameter_properties():
	return [
		{
			"doctype": "Property Setter",
			"doc_type": "Quality Feedback Parameter",
			"doctype_or_field": "DocField",
			"field_name": "feedback",
			"property": "hidden",
			"property_type": "Check",
			"value": "1",
		},
		{
			"doctype": "Property Setter",
			"doc_type": "Quality Feedback Parameter",
			"doctype_or_field": "DocField",
			"field_name": "rating",
			"property": "hidden",
			"property_type": "Check",
			"value": "1",
		},
		{
			"doctype": "Property Setter",
			"doc_type": "Quality Feedback Parameter",
			"doctype_or_field": "DocField",
			"field_name": "rating",
			"property": "reqd",
			"property_type": "Check",
			"value": "0",
		},
		{
			"doctype": "Property Setter",
			"doc_type": "Quality Feedback Parameter",
			"doctype_or_field": "DocField",
			"field_name": "parameter",
			"property": "label",
			"property_type": "Data",
			"value": "Survey Question",
		},
	]
