def get_asset_movement_custom_fields():
    return {
        "Asset Movement": [
            {
                "fieldname": "delivery_receipt",
                "fieldtype": "Attach",
                "insert_after": "assets",
                "label": "Delivery Receipt"
            },
            {
                "fieldname": "rfm_reference",
                "fieldtype": "Link",
                "label": "Request for Material",
                "options": "Request for Material",
                "read_only": 1,
                "print_hide": 1,
                "no_copy": 1,
            }
        ]
    }
