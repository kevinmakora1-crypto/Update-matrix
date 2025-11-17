import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from one_fm.custom.custom_field.shift_assignment import get_shift_assignment_custom_fields

def execute():
    custom_fields = get_shift_assignment_custom_fields()
    create_custom_fields(custom_fields)
