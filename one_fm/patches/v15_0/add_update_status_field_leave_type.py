from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from one_fm.one_fm.custom.custom_field.leave_type import get_leave_type_custom_fields


def execute():
	create_custom_fields(get_leave_type_custom_fields())