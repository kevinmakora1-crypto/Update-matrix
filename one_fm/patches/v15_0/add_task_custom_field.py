import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from one_fm.custom.custom_field.task import get_task_custom_fields

def execute():
    try:
        frappe.db.sql("DELETE from `tabCustom Field` WHERE name = 'Task-total_expense_claim' ")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error occurred while deleting total expense field in TASK")

    create_custom_fields(get_task_custom_fields())
