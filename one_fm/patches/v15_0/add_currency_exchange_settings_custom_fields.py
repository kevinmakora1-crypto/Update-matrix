from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from one_fm.custom.custom_field.currency_exchange_settings import get_currency_exchange_settings_custom_fields


def execute():
    create_custom_fields(get_currency_exchange_settings_custom_fields())