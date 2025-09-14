import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from one_fm.custom.property_setter.loan_product import get_loan_product_properties

def execute():
    make_property_setter(**get_loan_product_properties())