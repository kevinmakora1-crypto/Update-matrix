import frappe


def execute():    
    update_asset_owner_options()
    set_calculate_depreciation_readonly()
    

def update_asset_owner_options():
    property_setter_name = "Asset-asset_owner-options"
    
    if frappe.db.exists("Property Setter", property_setter_name):
        property_setter = frappe.get_doc("Property Setter", property_setter_name)
        
        current_options = property_setter.value or ""
        options_list = [opt.strip() for opt in current_options.split("\n") if opt.strip()]
        
        if "Customer" not in options_list:
            options_list.append("Customer")
            property_setter.value = "\n".join(options_list)
            property_setter.save()
            
            print(f"Updated {property_setter_name}: {property_setter.value}")
    else:
        frappe.make_property_setter({
            "doctype": "Asset",
            "fieldname": "asset_owner",
            "property": "options",
            "value": "Company\nSupplier\nCustomer",
            "property_type": "Text"
        })
        
        print(f"Created new Property Setter for Asset-asset_owner-options")


def set_calculate_depreciation_readonly():
    property_setter_name = "Asset-calculate_depreciation-read_only_depends_on"
    
    if frappe.db.exists("Property Setter", property_setter_name):
        property_setter = frappe.get_doc("Property Setter", property_setter_name)
        
        if property_setter.value != "eval:doc.custom_is_refundable":
            property_setter.value = "eval:doc.custom_is_refundable"
            property_setter.save()
            
            print(f"Updated {property_setter_name}: {property_setter.value}")
        else:
            print(f"{property_setter_name} already set correctly")
    else:
        frappe.make_property_setter({
            "doctype": "Asset",
            "fieldname": "calculate_depreciation",
            "property": "read_only_depends_on",
            "value": "eval:doc.custom_is_refundable",
            "property_type": "Check"
        })
        
        print(f"Created new Property Setter for Asset-calculate_depreciation-read_only_depends_on")
    
    frappe.db.commit()