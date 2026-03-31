"""
Patch to create standard Offer Term records required by the Job Offer workflow.

The `offer_term` field in the `Job Offer Term` child table is a mandatory Link field
pointing to the `Offer Term` DocType. When records like "Annual Leave" and "Probation Period"
don't exist in that DocType, Frappe throws a "Could not find Row #X: Offer Term: ..." error
whenever a Job Offer is saved or submitted.

This patch ensures all standard terms used by one_fm's Job Offer automation are present.
"""
import frappe


STANDARD_OFFER_TERMS = [
    "Mobile with Line",
    "Health Insurance",
    "Company Insurance",
    "Personal Laptop",
    "Personal Vehicle",
    "Accommodation",
    "Transportation",
    "Working Hours",
    "Annual Leave",
    "Probation Period",
    "Kuwait Visa processing Fees",
    "Kuwait Residency Fees",
    "Kuwait insurance Fees",
]


def execute():
    created = []
    for term_name in STANDARD_OFFER_TERMS:
        if not frappe.db.exists("Offer Term", term_name):
            doc = frappe.get_doc({
                "doctype": "Offer Term",
                "offer_term": term_name,
            })
            doc.insert(ignore_permissions=True)
            created.append(term_name)

    frappe.db.commit()

    if created:
        print(f"Created {len(created)} Offer Term records: {', '.join(created)}")
    else:
        print("All standard Offer Terms already exist — no changes made.")
