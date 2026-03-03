import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from one_fm.custom.custom_field.hd_ticket import get_hd_ticket_custom_fields

def execute():
    create_custom_fields(get_hd_ticket_custom_fields(), update=True)
