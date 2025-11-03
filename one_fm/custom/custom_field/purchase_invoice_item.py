def get_purchase_invoice_item_custom_fields():
    return {
        "Purchase Invoice Item": [
            {
                
                "fieldname": "custom_refundable",
                "label": "Refundable",
                "fieldtype": "Check",
                "insert_after": "rate_with_margin",
                "read_only": 1
            },
            { 
                "fieldname": "custom_margin_known",
                "label": "Margin Known?",
                "fieldtype": "Select",
                "insert_after": "custom_refundable",
                "read_only": 1,
                "options": "Yes\nNo\n "
            },
            { 
                "fieldname": "custom_pending_si_quantity",
                "label": "Pending SI Quantity",
                "fieldtype": "Float",
                "insert_after": "material_request_item",
                "read_only": 1,

            },

        ]
    }
