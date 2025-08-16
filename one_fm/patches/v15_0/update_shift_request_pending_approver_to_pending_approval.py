import frappe
from frappe.utils.fixtures import sync_fixtures


def execute():
    sync_fixtures("one_fm") 
    pending_worflows = frappe.get_all(
        "Shift Request",
        filters={"workflow_state": "Pending Approver"},
        fields=["name", "parent"]
    )
    if pending_worflows:
        update_existing_pending_approver_to_pending_approval(pending_worflows)

def update_existing_pending_approver_to_pending_approval(pending_worflows):
    for pending_worflow in pending_worflows:
        try:
            doc = frappe.get_doc("Shift Request", pending_worflow["name"])
            doc.workflow_state = "Pending Approval"
            doc.save()
            frappe.db.commit()     
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), f"Failed to update {pending_worflow['name']}")
