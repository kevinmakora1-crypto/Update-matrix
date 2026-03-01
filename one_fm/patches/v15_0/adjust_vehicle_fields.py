import frappe
from one_fm.setup.setup import add_property_setter
from one_fm.custom.property_setter.vehicle import get_vehicle_properties

def execute():
    add_property_setter(get_vehicle_properties())
