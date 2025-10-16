import frappe

def execute():
    """Update Item Workflow State For items which has disabled checkbox unchecked"""
    items = frappe.get_all("Item", filters={"disabled": 0,'workflow_state':['!=',"Approved"]}, pluck="name")
    for item in items:
        frappe.db.set_value("Item", item, "workflow_state", "Approved")