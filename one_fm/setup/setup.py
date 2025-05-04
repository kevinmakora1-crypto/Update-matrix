from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    create_custom_fields(get_custom_fields())

def get_custom_fields():
    custom_fields = {}
    custom_fields.update(get_job_applicant_custom_fields())
    return custom_fields

def get_job_applicant_custom_fields():
    return {
        "Job Applicant": [
            {
                "fieldname": "application_date",
                "fieldtype": "Datetime",
                "label": "Application Date",
                "insert_after": "country",
                "read_only": 1,
            },
        ]
    }
