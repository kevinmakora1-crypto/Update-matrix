import frappe

def execute():
    """
    Update Purchase Order Item descriptions from Item master for POs modified in last 30 days
    """
    po_items = frappe.db.sql("""
        SELECT 
            poi.name,
            poi.item_code,
            poi.description as current_description,
            item.description as item_description
        FROM `tabPurchase Order Item` poi
        INNER JOIN `tabPurchase Order` po ON po.name = poi.parent
        INNER JOIN `tabItem` item ON item.name = poi.item_code
        WHERE po.modified >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        AND (poi.description != item.description OR poi.description IS NULL)
    """, as_dict=1)
    
    if not po_items:
        print("No Purchase Order Items to update")
        return
    
    print(f"Found {len(po_items)} Purchase Order Items to update")
    
    for item in po_items:
        try:
            frappe.db.set_value(
                "Purchase Order Item",
                item.name,
                "description",
                item.item_description,
                update_modified=False
            )
            print(f"Updated {item.name}: {item.item_code}")
        except Exception as e:
            print(f"Error updating {item.name}: {str(e)}")
            frappe.log_error(
                message=f"Error updating PO Item {item.name}: {str(e)}",
                title="PO Item Description Update Failed"
            )
    
    frappe.db.commit()
    print(f"Successfully updated {len(po_items)} Purchase Order Item descriptions")
