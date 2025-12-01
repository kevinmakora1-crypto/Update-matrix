from one_fm.setup.setup import add_property_setter
from one_fm.custom.property_setter.quality_feedback_parameter import get_quality_feedback_parameter_properties

def execute():
    add_property_setter(get_quality_feedback_parameter_properties())