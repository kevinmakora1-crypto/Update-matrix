import frappe
from frappe.utils import flt
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from one_fm.custom.custom_field.purchase_invoice import get_purchase_invoice_custom_fields

def execute():
    # Ensure custom fields are created
    create_custom_fields(get_purchase_invoice_custom_fields())

    # Initialize pending_si_quantity for existing Purchase Invoices
    purchase_invoices = frappe.get_all(
        "Purchase Invoice",
        filters={"docstatus": 1, "custom_refundable": 1},
        fields=["name"]
    )
    
    for pi in purchase_invoices:
        pi_doc = frappe.get_doc("Purchase Invoice", pi.name)
        
        for item in pi_doc.items:
            billed_qty = frappe.db.sql("""
                SELECT 
                    IFNULL(SUM(si_item.qty), 0) as qty
                FROM 
                    `tabSales Invoice Item` si_item
                INNER JOIN 
                    `tabSales Invoice` si ON si.name = si_item.parent
                WHERE 
                    si.docstatus = 1
                    AND si_item.custom_purchase_invoice_item = %s
            """, (item.name), as_dict=1)
            
            total_billed = billed_qty[0].qty if billed_qty else 0
            pending_qty = flt(item.qty) - flt(total_billed)
            pending_qty = max(pending_qty, 0)
            
            frappe.db.set_value(
                "Purchase Invoice Item",
                item.name,
                "custom_pending_si_quantity",
                pending_qty,
                update_modified=False
            )
        
        frappe.db.commit()
