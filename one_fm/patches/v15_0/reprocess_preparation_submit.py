import frappe
from frappe.utils import now_datetime

# Patch to reprocess on_submit methods for Preparation document PRE-2025-12-03-1598657
# Reason: This document requires reprocessing due to a previous processing error or missed workflow step.
def execute():
    doc_name = "PRE-2025-12-03-1598657"
    
    if not frappe.db.exists("Preparation", doc_name):
        print(f"Document {doc_name} does not exist. Skipping patch.")
        return
    # Check if the document exists before processing
    if not frappe.db.exists("Preparation", doc_name):
        frappe.log_error(
            f"Document {doc_name} does not exist.",
            "Preparation Patch Error"
        )
        print(f"Document {doc_name} does not exist.")
        return
    try:
        doc = frappe.get_doc("Preparation", doc_name)
        

        if doc.docstatus != 1:
            frappe.log_error(
                f"Document {doc_name} is not in submitted state. Current docstatus: {doc.docstatus}",
                "Preparation Patch Error"
            )
            print(f"Document {doc_name} is not submitted (docstatus: {doc.docstatus})")
            return
        

        doc.validate_mandatory_fields_on_submit()
        
        if not doc.submitted_by:
            doc.db_set('submitted_by', frappe.session.user, update_modified=False)
        if not doc.submitted_on:
            doc.db_set('submitted_on', now_datetime(), update_modified=False)

        doc.recall_create_work_permit_renewal()
        doc.recall_create_medical_insurance_renewal()
        doc.recall_create_moi_renewal_and_extend()
        doc.recall_create_paci()
        
        doc.send_notifications()
        
        frappe.db.commit()
        
        print(f"Successfully reprocessed on_submit methods for {doc_name}")
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(
            frappe.get_traceback(),
            f"Preparation Patch Error - {doc_name}"
        )
        print(f"Error processing {doc_name}: {str(e)}")
