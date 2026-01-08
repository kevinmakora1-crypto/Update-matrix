import frappe
from frappe.model.utils.rename_field import rename_field

def execute():
    # Rename fields in Project doctype
    if frappe.db.has_column("Project", "account_manager"):
        rename_field("Project", "account_manager", "project_manager")
    if frappe.db.has_column("Project", "manager_name"):
        rename_field("Project", "manager_name", "project_manager_name")

    # Migrate data in custom fields if needed (for custom_field table)
    frappe.db.commit()
