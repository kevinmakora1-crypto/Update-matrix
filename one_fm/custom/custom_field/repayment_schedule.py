def get_repayment_schedule_custom_fields():
    return {
        "Repayment Schedule": [
            {
                "label": "Amount Paid Via Additional Payment",
                "fieldname": "custom_amount_paid_via_additional_payment",
                "insert_after": "is_accrued",
                "fieldtype": "Currency",
                "description": "Amount from this repayment schedule that has been settled through additional payments made outside of regular salary deductions"
            }
        ]
    }