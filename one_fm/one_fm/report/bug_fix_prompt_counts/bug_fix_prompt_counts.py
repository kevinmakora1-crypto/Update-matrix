# Copyright (c) 2024, ONE FM and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns, data = [], []

    columns = [
        {"fieldname": "name", "label": "Ticket ID", "fieldtype": "Link", "options": "HD Ticket", "width": 100},
        {"fieldname": "subject", "label": "Subject", "fieldtype": "Data", "width": 200},
        {"fieldname": "planning_prompts_count", "label": "Planning Prompts Count", "fieldtype": "Int", "width": 150},
        {"fieldname": "execution_prompt_count", "label": "Execution Prompt Count", "fieldtype": "Int", "width": 150},
        {"fieldname": "custom_bug_buster", "label": "Bug Buster", "fieldtype": "Link", "options": "User", "width": 150},
        {"fieldname": "resolution", "label": "Resolution", "fieldtype": "Small Text", "width": 300},
    ]

    conditions = "WHERE ticket_type = 'Bug'"
    if filters.get("from_date") and filters.get("to_date"):
        conditions += f" AND creation BETWEEN '{filters.get('from_date')}' AND '{filters.get('to_date')}'"

    data = frappe.db.sql(f"""
        SELECT
            name,
            subject,
            planning_prompts_count,
            execution_prompt_count,
            custom_bug_buster,
            resolution
        FROM
            `tabHD Ticket`
        {conditions}
    """, as_dict=True)

    return columns, data
