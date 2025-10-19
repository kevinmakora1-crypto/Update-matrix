def get_purchase_receipt_custom_fields():
    return {
        "Purchase Receipt": [
            {
                "fieldname": "one_fm_attach_delivery_note",
                "label": "Attach Stamped and Signed Delivery Note",
                "fieldtype": "Attach",
                "insert_after": "terms"
            },
            {
                "label": "Request for Purchase",
                "fieldname": "custom_request_for_purchase",
                "insert_after": "set_posting_time",
                "fieldtype": "Link",
                "options": "Request for Purchase",
                "read_only": 1,
                },
                {
                "label": "Request for Material",
                "fieldname": "custom_request_for_material",
                "insert_after": "custom_request_for_purchase",
                "fieldtype": "Link",
                "options": "Request for Material",
                "read_only": 1,
                }
        ]
    }
