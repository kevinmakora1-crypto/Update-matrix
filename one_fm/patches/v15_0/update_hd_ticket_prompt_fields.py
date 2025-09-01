import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_fields = {
        "HD Ticket": [
            {
                "fieldname": "planning_prompts_count",
                "fieldtype": "Int",
                "label": "Planning Prompts Count",
                "insert_after": "resolution_date",
                "depends_on": "eval:doc.ticket_type == 'Bug'"
            },
            {
                "fieldname": "execution_prompt_count",
                "fieldtype": "Int",
                "label": "Execution Prompt Count",
                "insert_after": "planning_prompts_count",
                "depends_on": "eval:doc.ticket_type == 'Bug'"
            }
        ]
    }
    create_custom_fields(custom_fields)
