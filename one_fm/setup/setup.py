from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    create_custom_fields(get_custom_fields())

def get_custom_fields():
    custom_fields = {}
    custom_fields.update(get_leave_application_custom_fields())
    return custom_fields

def get_leave_application_custom_fields():
    return {
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
    }