import frappe

def execute():
    doctypes_to_update = ["Purchase Order Item", "Purchase Invoice Item", "Purchase Receipt Item"]
    fields_to_update = ["margin_type", "margin_rate_or_amount"]
    
    for doc_type in doctypes_to_update:
        for field_name in fields_to_update:
            property_setter_name = f"{doc_type}-{field_name}-read_only"
            
            if frappe.db.exists("Property Setter", property_setter_name):
                doc = frappe.get_doc("Property Setter", property_setter_name)
                doc.value = "1"
                doc.save(ignore_permissions=True)
                print(f"Updated: {property_setter_name}")
            else:
                doc = frappe.new_doc("Property Setter")
                doc.doctype_or_field = "DocField"
                doc.doc_type = doc_type
                doc.field_name = field_name
                doc.property = "read_only"
                doc.property_type = "Check"
                doc.value = "1"
                doc.is_system_generated = 0
                doc.insert(ignore_permissions=True)
                print(f"Created: {property_setter_name}")
            
            frappe.db.commit()
        
        frappe.clear_cache(doctype=doc_type)
    
    print("Successfully set margin fields as read-only in Purchase Order Item and Purchase Invoice Item")