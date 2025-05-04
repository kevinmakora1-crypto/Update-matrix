from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    create_custom_fields({
        "Job Applicant": [
            {
                "fieldname": "application_date",
                "fieldtype": "Datetime",
                "label": "Application Date",
                "insert_after": "country",
                "read_only": 1,
            }
        ]
    })
