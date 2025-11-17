def get_purchase_receipt_item_custom_fields():
    return {
        "Purchase Receipt Item": [
            {
                "fieldname": "is_customer_asset",
                "label": "Is Customer Asset",
                "fieldtype": "Check",
                "insert_after": "item_code"
            },
            {
                "fieldname": "supplier_batch_id",
                "label": "Supplier Batch ID",
                "fieldtype": "Data",
                "insert_after": "bom",
                "depends_on": "eval:!doc.is_fixed_asset",
                "translatable": 1
            },
            {
                "fieldname": "manufacturing_date",
                "label": "Manufacturing Date",
                "fieldtype": "Date",
                "insert_after": "supplier_batch_id",
                "depends_on": "eval:!doc.is_fixed_asset"
            },
            {
                "fieldname": "expiry_date",
                "label": "Expiry Date",
                "fieldtype": "Date",
                "insert_after": "manufacturing_date",
                "depends_on": "eval:!doc.is_fixed_asset"
            },
            {
                "label": "Refundable",
                "fieldname": "custom_refundable",
                "insert_after": "rate_with_margin",
                "fieldtype": "Check",
                "read_only": 1,
            },
            {
                "fieldname": "margin_known",
                "fieldtype": "Select",
                "label": "Margin Known",
                "options": "\nYes\nNo",
                "read_only": 1,
                "insert_after": "discount_and_margin_section"

            },
        ]
    }
