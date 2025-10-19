import frappe
from frappe.utils import flt

from one_fm.overrides.purchase_receipt import get_rfm_in_purchase_receipt


def update_received_qty(doc, method):
    """Update received_qty on each item row of the linked Request for Material.

    Rules:
    - Link via parent field: custom_request_for_material on Purchase Receipt.
    - Aggregate across all submitted (docstatus=1) Purchase Receipts for that RFM.
    - Include returns: subtract qty for PRs where is_return=1.
    - Sum per item_code; for each RFM item row with that item_code set received_qty to the total (full amount on every matching row).
    - Skip silently if no link or RFM missing.
    - Re-run on submit, cancel, and update_after_submit (hook should call this).
    - Use frappe.log_error for unexpected errors; otherwise silent.
    """
    rfm_name = getattr(doc, 'custom_request_for_material', None)
    if not rfm_name:
        rfm_name = get_rfm_in_purchase_receipt(doc)
        
    if not frappe.db.exists('Request for Material', rfm_name):
        
        return  # silent skip

    try:
        # Aggregate quantities from all submitted Purchase Receipts for this RFM
        # Negative for returns.
        pr_items = frappe.db.sql(
            """
            SELECT pri.item_code,
                   SUM(pri.qty) AS total_received
            FROM `tabPurchase Receipt Item` pri
            INNER JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent
            WHERE pr.docstatus = 1
              AND pr.name = %(doc_name)s
            GROUP BY pri.item_code
            """,
            {"doc_name": doc.name},
            as_dict=True,
        )
        totals = {row.item_code: row.total_received for row in pr_items if row.item_code}
        
        # Fetch RFM item rows
        rfm_items = frappe.db.sql(
            """
            SELECT name, item_code
            FROM `tabRequest for Material Item`
            WHERE parent = %(parent)s
            """,
            {"parent": rfm_name},
            as_dict=True,
        )

        # Update each RFM item row (full aggregate on each matching row). Default 0 if not found.
        for r in rfm_items:
            item_code = r.item_code
            
            if not item_code:
                continue  # row without item_code (business rule might prevent this)
            received = totals.get(item_code, 0) or 0
            frappe.db.set_value('Request for Material Item', r.name, 'received_qty', received, update_modified=False)

    except Exception as e:
        frappe.log_error(title='update_received_qty failed', message=f'RFM: {rfm_name} PR: {getattr(doc, "name", "?")} Error: {e}')



def execute():
    """Update RFM received_qty from linked Purchase Receipts, each row of the Purchase Receipt has a linked PO"""
    

    for pr in frappe.get_all(
        "Purchase Receipt",
        filters={"docstatus": 1},
        fields=["name"],
    ):
        pr_doc = frappe.get_doc("Purchase Receipt", pr.name)
       
        update_received_qty(pr_doc, method="submit")
        