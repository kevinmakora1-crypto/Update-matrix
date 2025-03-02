import frappe
from frappe import _
from frappe.utils import nowdate



def set_workflow_states(doc,old_doc):
    """Sets approval dates based on workflow state changes."""
    current_workflow_state = doc.workflow_state

    # If the workflow state didn't change, no action is needed
    if old_doc.workflow_state == current_workflow_state:
        return

    # Mapping workflow states to custom field names
    workflow_mapping = {
        "Pending Purchase Manager": "custom_purchase_officer_approval_date",
        "Pending Finance Approver": "custom_purchase_manager_approval_date",
    }

    # Set approval dates based on current workflow state
    if current_workflow_state in workflow_mapping:
        doc.db_set(workflow_mapping[current_workflow_state],nowdate())



def on_update(doc, event):
    """Handles the update event for the Purchase Order document."""
    #Check if workflow_state was changed, if it wasn't then we return,
    old_doc = doc.get_doc_before_save()
    if not old_doc:
        return
    if old_doc.workflow_state == doc.workflow_state:
        return
    # Check if both dates are present; if so, no action is needed.
    if doc.custom_purchase_officer_approval_date and doc.custom_purchase_manager_approval_date:
        return
    set_workflow_states(doc,old_doc)
    
    
def validate_purchase_uom(doc, method):
    for item in doc.items:
        query = """
            select
                uom
            from
                `tabUOM Conversion Detail`
            where
                parent = %s
        """
        uoms_list = frappe.db.sql(
            query,
            item.item_code,
            as_list=True,
        )
        uoms = [item for sublist in uoms_list for item in sublist]
        if uoms and len(uoms) > 0:
            if item.uom not in uoms:
                msg = "The selected UOM in the row {0} is not having any UOM conversion Details in the item {1}".format(item.idx, item.item_code)
                frappe.throw(_(msg))

@frappe.whitelist()
def filter_purchase_uoms(doctype, txt, searchfield, start, page_len, filters):
    # filter UOM in item lines by UOM Conversion Detail set in the item
	query = """
		select
            uom
        from
            `tabUOM Conversion Detail`
        where
            parent = %(item_code)s
			and uom like %(txt)s
			limit %(start)s, %(page_len)s"""
	return frappe.db.sql(query,
		{
			'item_code': filters.get("item_code"),
			'start': start,
			'page_len': page_len,
			'txt': "%%%s%%" % txt
		}
	)
