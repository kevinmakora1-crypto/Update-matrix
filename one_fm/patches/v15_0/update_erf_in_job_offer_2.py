import frappe


def execute():
    frappe.db.set_value("Job Offer", "HR-OFF-2024-00762", "one_fm_erf", "ERF-2024-00014")