import frappe

def execute():
    try:
        property_setter_name = "Attendance-status-options"
        
        if frappe.db.exists("Property Setter", property_setter_name):
            property_setter = frappe.get_doc("Property Setter", property_setter_name)
            
            property_setter.doctype_or_field = "DocField"
            property_setter.value = "Present\nAbsent\nOn Leave\nHalf Day\nWork From Home\nDay Off\nClient Day Off\nFingerprint Appointment\nMedical Appointment\nHoliday\nOn Hold"
            
            property_setter.save(ignore_permissions=True)
            print(f"Property Setter '{property_setter_name}' updated successfully")
        else:
            property_setter = frappe.get_doc({
                "doctype": "Property Setter",
                "name": property_setter_name,
                "doc_type": "Attendance",
                "doctype_or_field": "DocField",
                "field_name": "status",
                "property": "options",
                "property_type": "Select",
                "value": "Present\nAbsent\nOn Leave\nHalf Day\nWork From Home\nDay Off\nClient Day Off\nFingerprint Appointment\nMedical Appointment\nHoliday\nOn Hold",
                "is_system_generated": 1
            })
            property_setter.insert(ignore_permissions=True)
            print(f"Property Setter '{property_setter_name}' created successfully")
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(str(e), "Attendance Status Options Patch")
        raise