def get_vehicle_properties():
    return [
        {
            "doc_type": "Vehicle",
            "doctype_or_field": "DocType",
            "property": "image_field",
            "property_type": "Data",
            "value": "image"
        },
        {
            "doc_type": "Vehicle",
            "doctype_or_field": "DocType",
            "property": "quick_entry",
            "property_type": "Check",
            "value": "0"
        },
        {
            "doctype": "Vehicle",
            "fieldname": "employee",
            "property": "reqd",
            "value": "1",
            "property_type": "Check",
        },
        {
            "doctype": "Vehicle",
            "fieldname": "employee",
            "property": "fieldtype",
            "value": "Link",
            "property_type": "Select",
        },
        {
            "doctype": "Vehicle",
            "fieldname": "employee",
            "property": "options",
            "value": "Employee",
            "property_type": "Small Text",
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