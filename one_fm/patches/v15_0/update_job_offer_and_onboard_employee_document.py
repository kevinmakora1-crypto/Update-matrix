import frappe


def execute():
    onboard_employee_names = ["EMP-ONB-2022-00303"]

    job_offer_names = frappe.get_all(
        "Onboard Employee",
        filters={"name": ["in", onboard_employee_names]},
        pluck="job_offer"
    )

    job_offer_names = tuple(job_offer_names) if job_offer_names else ("",)

    frappe.db.sql("""
        UPDATE `tabOnboard Employee`
        SET provide_accommodation_by_company = 0, provide_transportation_by_company = 0
        WHERE name IN %(names)s
    """, {"names": tuple(onboard_employee_names)})

    if job_offer_names != ("",):
        frappe.db.sql("""
            UPDATE `tabJob Offer`
            SET one_fm_provide_accommodation_by_company = 0, one_fm_provide_transportation_by_company = 0
            WHERE name IN %(names)s
        """, {"names": job_offer_names})
