from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
import frappe

def execute():
    """
    Migrates data from old 'forth_name' fields to new 'fourth_name' fields
    instead of renaming the columns directly.
    """
    # Create custom fields for Job Applicant before migration
    create_custom_fields(get_job_applicant_custom_fields())

    # Job Applicant
    if frappe.db.has_column("Job Applicant", "one_fm_forth_name") and frappe.db.has_column("Job Applicant", "one_fm_fourth_name"):
        frappe.db.sql("UPDATE `tabJob Applicant` SET `one_fm_fourth_name` = `one_fm_forth_name` WHERE `one_fm_forth_name` IS NOT NULL")
    if frappe.db.has_column("Job Applicant", "one_fm_forth_name_in_arabic") and frappe.db.has_column("Job Applicant", "one_fm_fourth_name_in_arabic"):
        frappe.db.sql("UPDATE `tabJob Applicant` SET `one_fm_fourth_name_in_arabic` = `one_fm_forth_name_in_arabic` WHERE `one_fm_forth_name_in_arabic` IS NOT NULL")

    # Onboard Employee
    if frappe.db.has_column("Onboard Employee", "forth_name_in_arabic") and frappe.db.has_column("Onboard Employee", "fourth_name_in_arabic"):
        frappe.db.sql("UPDATE `tabOnboard Employee` SET `fourth_name_in_arabic` = `forth_name_in_arabic` WHERE `forth_name_in_arabic` IS NOT NULL")

    # Residency
    if frappe.db.has_column("Residency", "forth_name") and frappe.db.has_column("Residency", "fourth_name"):
        frappe.db.sql("UPDATE `tabResidency` SET `fourth_name` = `forth_name` WHERE `forth_name` IS NOT NULL")
    if frappe.db.has_column("Residency", "forth_name_in_arabic") and frappe.db.has_column("Residency", "fourth_name_in_arabic"):
        frappe.db.sql("UPDATE `tabResidency` SET `fourth_name_in_arabic` = `forth_name_in_arabic` WHERE `forth_name_in_arabic` IS NOT NULL")
        
    # Employee
    if frappe.db.has_column("Employee", "one_fm_forth_name") and frappe.db.has_column("Employee", "one_fm_fourth_name"):
        frappe.db.sql("UPDATE `tabEmployee` SET `one_fm_fourth_name` = `one_fm_forth_name` WHERE `one_fm_forth_name` IS NOT NULL")
    if frappe.db.has_column("Employee", "one_fm_forth_name_in_arabic") and frappe.db.has_column("Employee", "one_fm_fourth_name_in_arabic"):
        frappe.db.sql("UPDATE `tabEmployee` SET `one_fm_fourth_name_in_arabic` = `one_fm_forth_name_in_arabic` WHERE `one_fm_forth_name_in_arabic` IS NOT NULL")
        
    # Transfer Paper
    if frappe.db.has_column("Transfer Paper", "forth_name") and frappe.db.has_column("Transfer Paper", "fourth_name"):
        frappe.db.sql("UPDATE `tabTransfer Paper` SET `fourth_name` = `forth_name` WHERE `forth_name` IS NOT NULL")
    if frappe.db.has_column("Transfer Paper", "forth_name_in_arabic") and frappe.db.has_column("Transfer Paper", "fourth_name_in_arabic"):
        frappe.db.sql("UPDATE `tabTransfer Paper` SET `fourth_name_in_arabic` = `forth_name_in_arabic` WHERE `forth_name_in_arabic` IS NOT NULL")

    delete_forth_name_fields()

def get_job_applicant_custom_fields():
    return {
        "Job Applicant": [
            {
                "fieldname": "one_fm_fourth_name",
                "fieldtype": "Data",
                "label": "Fourth Name",
                "insert_after": "one_fm_third_name"
            },
            {
                "fieldname": "one_fm_fourth_name_in_arabic",
                "fieldtype": "Data",
                "label": "Fourth Name in Arabic",
                "insert_after": "one_fm_third_name_in_arabic"
            }
        ]
    }

def delete_forth_name_fields():
    # Delete forth_name custom fields from Job Applicant
    for field in ["one_fm_forth_name", "one_fm_forth_name_in_arabic"]:
        if frappe.db.has_column("Job Applicant", field):
            frappe.delete_doc("Custom Field", f"Job Applicant-{field}", force=1)
        if frappe.db.has_column("Employee", field):
            frappe.delete_doc("Custom Field", f"Employee-{field}", force=1)