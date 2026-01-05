def get_buying_settings_custom_fields():
    return {
        "Buying Settings": [
            {
                "default": "Yes",
                "label": "Can 'Purchase Order' be created from 'Request for Material' directly?",
                "description": "Controls whether Purchase Orders can be created directly from Request for Material without requiring a Request for Purchase.",
                "fieldname": "po_from_rfm",
                "fieldtype": "Select",
                "insert_after": "po_required",
                "options": "Yes\nNo"
            }
        ]
    }
