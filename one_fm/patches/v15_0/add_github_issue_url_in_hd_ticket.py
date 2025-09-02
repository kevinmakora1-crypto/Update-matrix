import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_field = {
        "HD Ticket": [
            {
                "fieldname": "custom_github_issue_url",
                "fieldtype": "Data",
                "label": "GitHub Issue",
                "insert_after": "custom_dev_ticket",
                "read_only": 1
            }
        ]
    }
    create_custom_fields(custom_field)