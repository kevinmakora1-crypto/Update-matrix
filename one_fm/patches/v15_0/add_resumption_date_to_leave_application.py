from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    create_custom_fields({
        "Leave Application": [
            {
                "fieldname": "resumption_date",
                "fieldtype": "Date",
                "label": "Resumption Date",
                "insert_after": "to_date",
                "description": "Select the date on which you will resume work",
                "reqd": 1
            }
        ]
    })