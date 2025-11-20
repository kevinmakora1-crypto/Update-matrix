def get_request_for_quotation_item_custom_fields():
    return {
        "Request for Quotation Item": [
            {
                "fieldname": "custom_request_for_material",
                "label": "Request for Material",
                "fieldtype": "Link",
                "options": "Request for Material",
                "insert_after": "material_request_item",
                "read_only": 1
            },
            {
                "fieldname": "custom_request_for_material_item",
                "label": "Request for Material Item",
                "fieldtype": "Link",
                "options": "Request for Material Item",
                "insert_after": "custom_request_for_material",
                "read_only": 1
            }
        ]
    }
