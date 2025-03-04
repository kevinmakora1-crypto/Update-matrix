import frappe

def execute():
    purchase_orders = frappe.db.sql(
        """
        SELECT name, one_fm_request_for_purchase 
        FROM `tabPurchase Order`
        WHERE one_fm_request_for_purchase IS NOT NULL 
        AND one_fm_request_for_purchase != ''
        AND docstatus = 1
        """,
        as_dict=True
    )

    if not purchase_orders:
        return  
    
    po_map = {po["name"]: po["one_fm_request_for_purchase"] for po in purchase_orders}
    po_names = list(po_map.keys())

    purchase_order_items = frappe.db.sql(
        """
        SELECT qty, item_code, parent 
        FROM `tabPurchase Order Item`
        WHERE parent IN %(po_names)s
        """,
        {"po_names": po_names},
        as_dict=True
    )

    if not purchase_order_items:
        return  
    
    update_queries = []
    update_values = []
    
    for item in purchase_order_items:
        request_for_purchase = po_map.get(item["parent"])
        if request_for_purchase:
            update_queries.append(
                """
                UPDATE `tabRequest for Purchase Item`
                SET purchased_quantity = %s
                WHERE parenttype = 'Request for Purchase'
                AND parent = %s
                AND item_code = %s
                """
            )
            update_values.append((item["qty"], request_for_purchase, item["item_code"]))

    if update_queries:
        for query, values in zip(update_queries, update_values):
            frappe.db.sql(query, values)

    frappe.db.commit() 
