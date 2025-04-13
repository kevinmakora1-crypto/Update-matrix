import frappe

def execute():
    # Update Employee record
    frappe.db.sql("""
        UPDATE `tabEmployee`
        SET job_offer = %s, job_applicant = %s
        WHERE name = %s
    """, ("HR-OFF-2025-00320", "HR-APP-2025-01529", "HR-EMP-03572"))

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

    frappe.db.commit()
