import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from one_fm.custom.custom_field.request_for_quotation_item import get_request_for_quotation_item_custom_fields

def execute():
    create_custom_fields(get_request_for_quotation_item_custom_fields())