import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from one_fm.custom.custom_field.sales_invoice_item import get_sales_invoice_item_custom_fields

def execute():
    create_custom_fields(get_sales_invoice_item_custom_fields())
