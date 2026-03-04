from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from one_fm.custom.custom_field.location import get_location_custom_fields

def execute():
    create_custom_fields(get_location_custom_fields())
