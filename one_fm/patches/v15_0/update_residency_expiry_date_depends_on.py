import frappe

def execute():
    custom_field = frappe.get_doc('Custom Field', 'Employee-residency_expiry_date')
    custom_field.depends_on = 'eval:doc.under_company_residency==1 and doc.pam_type != "Kuwaiti"'
    custom_field.save()
