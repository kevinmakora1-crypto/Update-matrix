def get_quality_feedback_template_parameter_custom_fields():
    return {
        "Quality Feedback Template Parameter": [
            {
                "fieldname": "custom_rating_scale",
                "fieldtype": "Link",
                "label": "Rating Scale",
                "options": "Rating Scale",
                "in_list_view": 1,
                "reqd": 1,
                "insert_after": "parameter"
            }
        ]
    }
