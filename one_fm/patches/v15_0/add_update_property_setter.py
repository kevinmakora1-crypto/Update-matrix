import frappe
from one_fm.setup import (
    get_field_properties, add_property_setter
)

def execute():
    add_property_setter(get_field_properties())
