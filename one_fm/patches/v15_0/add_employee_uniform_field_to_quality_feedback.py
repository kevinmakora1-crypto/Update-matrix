import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_fields = {
        "Quality Feedback": [
            {
                "label": "Employee Uniform",
                "fieldname": "employee_uniform",
                "insert_after": "custom_quantity",
                "fieldtype": "Link",
                "options": "Employee Uniform",
                "read_only": 1,
                "in_standard_filter": 1
            }
        ]
    }
    create_custom_fields(custom_fields)
