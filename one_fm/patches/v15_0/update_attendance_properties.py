from one_fm.setup.setup import add_property_setter
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from one_fm.custom.property_setter.attendance import get_attendance_properties
from one_fm.custom.custom_field.attendance import get_attendance_custom_fields

def execute():
    add_property_setter(get_attendance_properties())
    create_custom_fields(get_attendance_custom_fields())