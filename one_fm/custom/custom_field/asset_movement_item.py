def get_asset_movement_custom_fields():
    return {
        "Asset Movement Item": [
            {
                "fieldname": "delivery_receipt",
                "fieldtype": "Attach",
                "insert_after": "assets",
                "label": "Delivery Receipt"
            },
            {
                "fieldname": "rfm_item_reference",
                "fieldtype": "Link",
                "label": "Request for Material Item",
                "options": "Request for Material Item",
                "read_only": 1,
                "print_hide": 1,
                "no_copy": 1,
            },
            {
                "fieldname": "rfm_item_code",
                "fieldtype": "Link",
                "label": "RFM Item Code",
                "options": "Item",
                "read_only": 1,
                "print_hide": 1,
                "no_copy": 1,
            }
        ]
    }
