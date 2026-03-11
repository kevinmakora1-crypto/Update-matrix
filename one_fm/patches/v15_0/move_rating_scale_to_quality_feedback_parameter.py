import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from one_fm.setup.setup import delete_custom_fields
from one_fm.custom.custom_field.quality_feedback_template import get_quality_feedback_template_custom_fields
from one_fm.custom.custom_field.quality_feedback_template_parameter import get_quality_feedback_template_parameter_custom_fields

def execute():
    fields_to_delete = {
        "Quality Feedback Template": [
            {
                "fieldname": "custom_rating_scale",
            }
        ]
    }
    delete_custom_fields(fields_to_delete)

    create_custom_fields(get_quality_feedback_template_custom_fields())
    create_custom_fields(get_quality_feedback_template_parameter_custom_fields())
