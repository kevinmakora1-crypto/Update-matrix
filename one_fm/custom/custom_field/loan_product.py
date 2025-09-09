def get_loan_product_custom_fields():
    return {
        "Loan Product": [
            {
                "label": "Maximum Salary Threshold",
                "fieldname": "custom_maximum_salary_threshold",
                "insert_after": "maximum_loan_amount",
                "fieldtype": "Currency",
                "reqd": 1,
                "description": "Loan will not be allowed for monthly salary exceeding this number"
            }
        ]
    }