import frappe


def execute():
    property_setter_name = "Asset-asset_owner-options"
    
    if frappe.db.exists("Property Setter", property_setter_name):
        property_setter = frappe.get_doc("Property Setter", property_setter_name)
        
        current_options = property_setter.value or ""
        options_list = [opt.strip() for opt in current_options.split("\n") if opt.strip()]
        
        if "Customer" not in options_list:
            options_list.append("Customer")
            property_setter.value = "\n".join(options_list)
            property_setter.save()
            frappe.db.commit()
            
            print(f"Updated {property_setter_name}: {property_setter.value}")
    else:
        frappe.make_property_setter({
            "doctype": "Asset",
            "fieldname": "asset_owner",
            "property": "options",
            "value": "Company\nSupplier\nCustomer",
            "property_type": "Text"
        })
        frappe.db.commit()
        
        print(f"Created new Property Setter for Asset-asset_owner-options")