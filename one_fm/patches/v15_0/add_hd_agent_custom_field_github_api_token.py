import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_field = {
        "HD Agent": [
            {
                "fieldname": "github_api_token",
                "fieldtype": "Password",
                "label": "GitHub API Token",
                "insert_after": "agent_name",
                "description": "GitHub API Token for creating issues on behalf of the user"
            }
            
        ]
    }
    create_custom_fields(custom_field)