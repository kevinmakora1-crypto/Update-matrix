from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from one_fm.custom.custom_field.shift_request import get_shift_request_custom_fields


def execute():
    create_custom_fields(get_shift_request_custom_fields())