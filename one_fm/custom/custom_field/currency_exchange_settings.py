def get_currency_exchange_settings_custom_fields():
    return {
        "Currency Exchange Settings": [
            {
                "fieldname": "currencies_section",
                "fieldtype": "Section Break",
                "label": "Currencies",
                "insert_after": "result_key"
            },
            {
                "fieldname": "business_currencies",
                "fieldtype": "Table MultiSelect",
                "label": "Business Currencies",
                "options": "Business Currency",
                "insert_after": "currencies_section"
            }
        ]
    }
