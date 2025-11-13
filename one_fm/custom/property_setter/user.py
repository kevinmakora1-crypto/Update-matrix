def get_user_properties():
    return [
        {
            "doctype": "Property Setter",
            "doc_type": "User",
            "doctype_or_field": "DocType",
            "property": "title_field",
            "property_type": "Data",
            "value": "full_name",
        },
        {
            "doctype": "Property Setter",
            "doc_type": "User",
            "doctype_or_field": "DocType",
            "property": "show_title_field_in_link",
            "property_type": "Check",
            "value": "1",
        },
    ]
