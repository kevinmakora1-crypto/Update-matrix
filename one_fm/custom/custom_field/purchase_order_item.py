def get_purchase_order_item_custom_fields():
    return {
        "Purchase Order Item": [
            {
                "fieldname": "request_for_material_item",
                "label": "Request for Material Item",
                "fieldtype": "Data",
                "insert_after": "material_request_item",
                "hidden": 1,
                "read_only": 1,
                "translatable": 1
            },
            {
                "default": "0",
                "fieldname": "is_refundable",
                "fieldtype": "Check",
                "in_standard_filter": 1,
                "read_only": 1,
                "label": "Refundable",
                "insert_after": "rate_with_margin"
            },
            {
                "fieldname": "request_for_material",
                "label": "Request for Material",
                "fieldtype": "Link",
                "insert_after": "material_request",
                "options": "Request for Material"
            },
            {
                "fieldname": "is_customer_asset",
                "label": "Is Customer Asset",
                "fieldtype": "Check",
                "insert_after": "item_code"
            }
        ]
    }
