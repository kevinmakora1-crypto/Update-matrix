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
        "inform_the_costing_to",
        "costing_print_format"
    ]
    
    for field in fields_to_transfer:
        if hasattr(grd_settings, field):
            value = getattr(grd_settings, field)
            if value:
                setattr(hr_settings, field, value)
    
    if hasattr(grd_settings, 'renewal_extension_cost') and grd_settings.renewal_extension_cost:
        hr_settings.renewal_extension_cost = []
        for row in grd_settings.renewal_extension_cost:
            hr_settings.append("renewal_extension_cost", {
                "renewal_or_extend": row.renewal_or_extend,
                "no_of_years": row.no_of_years,
                "work_permit_amount": row.work_permit_amount,
                "medical_insurance_amount": row.medical_insurance_amount,
                "residency_stamp_amount": row.residency_stamp_amount,
                "civil_id_amount": row.civil_id_amount,
                "total_amount": row.total_amount
            })
    
    hr_settings.flags.ignore_mandatory = True
    hr_settings.save()
    
    frappe.db.commit()