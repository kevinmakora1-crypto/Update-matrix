import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from one_fm.custom.custom_field.hr_settings import get_hr_settings_custom_fields

def execute():
    custom_fields = get_hr_settings_custom_fields()
    create_custom_fields(custom_fields)
