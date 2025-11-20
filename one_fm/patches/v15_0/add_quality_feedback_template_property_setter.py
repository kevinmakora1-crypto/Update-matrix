from one_fm.setup.setup import add_property_setter
from one_fm.custom.property_setter.quality_feedback_template import get_quality_feedback_template_properties

def execute():
    add_property_setter(get_quality_feedback_template_properties())