from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from one_fm.custom.custom_field.buying_settings import get_buying_settings_custom_fields

def execute():
    create_custom_fields(get_buying_settings_custom_fields())

