from one_fm.custom.property_setter.user import get_user_properties
from one_fm.setup.setup import add_property_setter

def execute():
    add_property_setter(get_user_properties())
