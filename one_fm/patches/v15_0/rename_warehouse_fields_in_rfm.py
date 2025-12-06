import frappe
from frappe.model.utils.rename_field import rename_field


def execute():
	frappe.reload_doc("one_fm", "doctype", "request_for_material")

	try:
		rename_field("Request for Material", "warehouse", "source_warehouse")
		rename_field("Request for Material", "t_warehouse", "target_warehouse")

	except Exception as e:
		if e.args[0] != 1054:
			raise