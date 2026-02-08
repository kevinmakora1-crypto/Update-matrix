from one_fm.custom.property_setter.leave_application import get_leave_application_properties
from one_fm.setup.setup import add_property_setter

def execute():
	add_property_setter(get_leave_application_properties())
