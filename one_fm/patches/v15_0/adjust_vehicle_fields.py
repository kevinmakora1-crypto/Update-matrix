import frappe
from one_fm.setup.setup import add_property_setter

def execute():
    properties = [
        {
            "doctype": "Vehicle",
            "fieldname": "employee",
            "property": "reqd",
            "value": "1",
            "property_type": "Check",
        },
        {
            "doctype": "Vehicle",
            "fieldname": "location",
            "property": "label",
            "value": "Vehicle Location",
            "property_type": "Data",
        },
        {
            "doctype": "Vehicle",
            "fieldname": "location",
            "property": "fieldtype",
            "value": "Link",
            "property_type": "Select",
        },
        {
            "doctype": "Vehicle",
            "fieldname": "location",
            "property": "options",
            "value": "Location",
            "property_type": "Small Text",
        },
        {
            "doctype": "Vehicle",
            "fieldname": "location",
            "property": "reqd",
            "value": "1",
            "property_type": "Check",
        },
    ]
    add_property_setter(properties)
    frappe.clear_cache(doctype="Vehicle")
