import frappe
from frappe.model.utils.rename_field import rename_field
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from one_fm.custom.custom_field.project import get_project_custom_fields

def execute():
    create_custom_fields(get_project_custom_fields())
    query = """
        UPDATE `tabProject`
        SET project_manager = account_manager,
            project_manager_name = manager_name
        WHERE account_manager IS NOT NULL OR manager_name IS NOT NULL
    """
    frappe.db.sql(query)
    frappe.db.delete("Custom Field", {"dt": "Project", "fieldname": "account_manager"})
    frappe.db.delete("Custom Field", {"dt": "Project", "fieldname": "manager_name"})
    # Migrate data in custom fields if needed (for custom_field table)
    frappe.db.commit()
