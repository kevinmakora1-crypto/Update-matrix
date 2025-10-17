import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_fields = {
        "Project": [
            {
            "label": "Success Metrics",
            "fieldname": "custom_success_metrics",
            "insert_after": "custom_success_and_completion_criteria",
            "fieldtype": "Text",
            "description": "Define the metric of success",
            }
        ]
    }
    create_custom_fields(custom_fields)
    