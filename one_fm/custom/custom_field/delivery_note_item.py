def get_delivery_note_item_custom_fields():
    return {
        "Delivery Note Item": [
            {
                "fieldname": "site",
                "fieldtype": "Link",
                "insert_after": "target_warehouse",
                "label": "Site",
                "options": "Operations Site"
            }
        ]
    }
