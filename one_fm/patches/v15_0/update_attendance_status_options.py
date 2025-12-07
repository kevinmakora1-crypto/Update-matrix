import frappe
from one_fm.setup.setup import add_property_setter
from one_fm.custom.property_setter.attendance import get_attendance_properties

def execute():
    add_property_setter(get_attendance_properties())