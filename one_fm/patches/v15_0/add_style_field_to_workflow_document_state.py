import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_fields = {
        "Workflow Document State": [
            {
                "fieldname": "style",
                "fieldtype": "Data",
                "label": "Style",
                "insert_after": "update_value",
                "fetch_from": "state.style"
            }
        ]
    }
    create_custom_fields(custom_fields)
