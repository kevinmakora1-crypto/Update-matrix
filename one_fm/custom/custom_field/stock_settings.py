def get_stock_settings_custom_fields():
    return {
        "Stock Settings": [
            {
                "fieldname": "quality_feedback_settings",
                "fieldtype": "Section Break",
                "label": "Quality Feedback Settings",
                "insert_after": "allow_to_make_quality_inspection_after_purchase_or_delivery"
            },
            {
                "fieldname": "quality_feedback_form_languages",
                "fieldtype": "Table MultiSelect",
                "label": "Quality Feedback Form Languages",
                "options": "Quality Feedback Form Language",
                "description": "The selected languages can be used in the Quality Feedback Form",
                "insert_after": "quality_feedback_settings"
            }
        ]
    }
