import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    # Add custom fields to Asset Movement and Asset Movement Item
    create_custom_fields({
        "Asset Movement": [
            {
                "fieldname": "request_for_material",
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
                "fieldname": "request_for_material_item",
                "fieldtype": "Link",
                "label": "Request for Material Item",
                "options": "Request for Material Item",
                "read_only": 1,
                "print_hide": 1,
                "no_copy": 1,
            }
        ]
    })
