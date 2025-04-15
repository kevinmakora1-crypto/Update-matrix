import frappe

from one_fm.hiring.utils import update_erf_close_with

def execute():
    # Update Employee record
    frappe.db.sql("""
        UPDATE `tabEmployee`
        SET job_offer = %s, job_applicant = %s, one_fm_erf = %s
        WHERE name = %s
    """, ("HR-OFF-2025-00320", "HR-APP-2025-01529", "ERF-2024-00052", "HR-EMP-03572"))

    # Update Onboard Employee record
    frappe.db.sql("""
        UPDATE `tabOnboard Employee`
        SET employee = %s
        WHERE name = %s
    """, ("HR-EMP-03572", "EMP-ONB-2025-00137"))

    # Update Duty Commencement record
    frappe.db.sql("""
        UPDATE `tabDuty Commencement`
        SET employee = %s
        WHERE name = %s
    """, ("HR-EMP-03572", "DC-2025-00158"))

    update_erf_close_with(frappe.get_doc("Employee", "HR-EMP-03572"))

    frappe.db.commit()


