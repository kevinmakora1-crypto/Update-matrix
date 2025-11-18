import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    # Add custom fields to Asset Movement and Asset Movement Item
    create_custom_fields({
        "Asset Movement": [
            {
                "fieldname": "rfm_reference",
                "fieldtype": "Link",
                "label": "Request for Material",
                "options": "Request for Material",
                "read_only": 1,
                "print_hide": 1,
                "no_copy": 1,
            }
        ],
        "Asset Movement Item": [
            {
                "fieldname": "rfm_item_reference",
                "fieldtype": "Link",
                "label": "Request for Material Item",
                "options": "Request for Material Item",
                "read_only": 1,
                "print_hide": 1,
                "no_copy": 1,
            },
            {
                "fieldname": "rfm_item_code",
                "fieldtype": "Link",
                "label": "RFM Item Code",
                "options": "Item",
                "read_only": 1,
                "print_hide": 1,
                "no_copy": 1,
            }
        ]
    })
