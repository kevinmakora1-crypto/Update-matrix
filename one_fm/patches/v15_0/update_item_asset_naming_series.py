import frappe

def execute():
    update_asset_naming_series_options()
    update_asset_naming_series_default()
    frappe.db.commit()

def update_asset_naming_series_options():
    property_setter_name = "Item-asset_naming_series-options"
    
    if frappe.db.exists("Property Setter", property_setter_name):
        existing_value = frappe.db.get_value("Property Setter", property_setter_name, "value")
        
        if "ACC-ASS-.YYYY.-" not in existing_value:
            new_value = existing_value + "\nACC-ASS-.YYYY.-"
            frappe.db.set_value("Property Setter", property_setter_name, "value", new_value)
            print(f"Updated existing Property Setter: {property_setter_name}")
        else:
            print(f"ACC-ASS-.YYYY.- already exists in options")
    else:
        frappe.get_doc({
            "doctype": "Property Setter",
            "doctype_or_field": "DocField",
            "doc_type": "Item",
            "field_name": "asset_naming_series",
            "property": "options",
            "property_type": "Text",
            "value": "ACC-ASS-.YYYY.-"
        }).insert(ignore_permissions=True)
        print(f"Created Property Setter: {property_setter_name}")

def update_asset_naming_series_default():
    property_setter_name = "Item-asset_naming_series-default"
    
    if frappe.db.exists("Property Setter", property_setter_name):
        frappe.db.set_value("Property Setter", property_setter_name, "value", "ACC-ASS-.YYYY.-")
        print(f"Updated existing Property Setter: {property_setter_name}")
    else:
        frappe.get_doc({
            "doctype": "Property Setter",
            "doctype_or_field": "DocField",
            "doc_type": "Item",
            "field_name": "asset_naming_series",
            "property": "default",
            "property_type": "Text",
            "value": "ACC-ASS-.YYYY.-"
        }).insert(ignore_permissions=True)
        print(f"Created Property Setter: {property_setter_name}")
