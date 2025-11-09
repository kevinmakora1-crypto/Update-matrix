def get_payment_schedule_custom_fields():
    return {
        "Payment Schedule": [
            {
                "fieldname": "one_fm_payment",
                "fieldtype": "Select",
                "insert_after": "mode_of_payment",
                "label": "Payment",
                "fetch_from": "payment_term.one_fm_payment",
                "options": "\nIn Advance\nOn Delivery",
                "translatable": 1
            }
        ]
    }
