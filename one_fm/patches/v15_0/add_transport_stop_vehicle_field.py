from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from one_fm.custom.custom_field.vehicle import get_vehicle_custom_fields

def execute():
    create_custom_fields(get_vehicle_custom_fields())
