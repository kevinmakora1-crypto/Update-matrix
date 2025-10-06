import frappe

def execute():
    if not frappe.db.exists("DocType", "GRD Settings"):
        return
    
    grd_settings = frappe.get_single("GRD Settings")
    hr_settings = frappe.get_single("HR Settings")
    

    fields_to_transfer = [
        "default_grd_supervisor",
        "default_grd_operator",
        "default_grd_operator_pifss",
        "default_grd_operator_transfer",
        "default_pam_operator",
        "days_before_expiry_to_notify_supervisor",
        "preparation_record_creation_day",
        "last_preparation_record_created_on",
        "last_preparation_record_created_by",
        "inform_the_costing_to",
        "costing_print_format"
    ]
    
    # Transfer values
    for field in fields_to_transfer:
        if hasattr(grd_settings, field):
            value = getattr(grd_settings, field)
            if value:
                setattr(hr_settings, field, value)
    
    hr_settings.flags.ignore_mandatory = True
    hr_settings.save()
    
    frappe.db.commit()