import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    if not frappe.db.exists("Custom Field", "Employee-site_supervisor_name"):
        create_custom_fields({
            "Employee": [
                {
                    "fieldname": "site_supervisor_name",
                    "owner":"Administrator",
                    "fieldtype": "Data",
                    "label": "Site Supervisor Name",
                    "insert_after": "site",
                    "fetch_from":"site.account_supervisor_name",
                    "read_only": 1,
                },
            ]
        })
    if not frappe.db.exists("Custom Field", "Employee-project_manager_name"):
        create_custom_fields({
            "Employee": [
                {
                    "fieldname": "project_manager_name",
                    "owner":"Administrator",
                    "fieldtype": "Data",
                    "label": "Project Manager Name",
                    "insert_after": "project",
                    "fetch_from":"project.manager_name",
                    "read_only": 1,
                },
            ]
        })
