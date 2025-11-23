from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from one_fm.custom.custom_field.quality_feedback_template import get_quality_feedback_template_custom_fields


def execute():
	create_custom_fields(get_quality_feedback_template_custom_fields())
