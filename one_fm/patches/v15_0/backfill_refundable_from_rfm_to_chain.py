import frappe

def execute():
    frappe.db.auto_commit_on_many_writes = True
    
    print("Starting refundable field backfill from RFM to procurement chain...")
    
    # Get all refundable RFMs
    refundable_rfms = frappe.db.sql("""
        SELECT name, is_refundable
        FROM `tabRequest for Material`
        WHERE is_refundable = 1
    """, as_dict=1)
    
    print(f"Found {len(refundable_rfms)} refundable RFMs")
    
    rfp_updated = 0
    po_updated = 0
    pr_updated = 0
    
    affected_docs = {
        'rfp': [],
        'po': [],
        'pr': []
    }
    
    for rfm in refundable_rfms:
        # Get linked RFPs
        rfps = frappe.db.sql("""
            SELECT name, is_refundable
            FROM `tabRequest for Purchase`
            WHERE request_for_material = %s
            AND (is_refundable IS NULL OR is_refundable = 0)
        """, rfm.name, as_dict=1)

        
        for rfp in rfps:
            frappe.db.set_value("Request for Purchase", rfp.name, "is_refundable", 1, update_modified=False)
            rfp_updated += 1
            affected_docs['rfp'].append({
                'rfm': rfm.name,
                'rfp': rfp.name,
                'old_value': rfp.is_refundable or 0
            })
            
            # Get linked Purchase Orders
            pos = frappe.db.sql("""
                SELECT name, is_refundable
                FROM `tabPurchase Order`
                WHERE one_fm_request_for_purchase = %s
                AND (is_refundable IS NULL OR is_refundable = 0)
            """, rfp.name, as_dict=1)
            
            for po in pos:
                frappe.db.set_value("Purchase Order", po.name, "is_refundable", 1, update_modified=False)
                po_updated += 1
                affected_docs['po'].append({
                    'rfm': rfm.name,
                    'rfp': rfp.name,
                    'po': po.name,
                    'old_value': po.is_refundable or 0
                })
        
        # Get Purchase Receipts linked directly to RFM
        prs_from_rfm = frappe.db.sql("""
            SELECT name, custom_refundable
            FROM `tabPurchase Receipt`
            WHERE custom_request_for_material = %s
            AND (custom_refundable IS NULL OR custom_refundable = 0)
        """, rfm.name, as_dict=1)
        
        for pr in prs_from_rfm:
            frappe.db.set_value("Purchase Receipt", pr.name, "custom_refundable", 1, update_modified=False)
            pr_updated += 1
            affected_docs['pr'].append({
                'rfm': rfm.name,
                'rfp': None,
                'po': None,
                'pr': pr.name,
                'old_value': pr.custom_refundable or 0,
                'linked_via': 'custom_request_for_material'
            })
        
        # Get Purchase Receipts linked via RFP (if any RFPs exist)
        for rfp in rfps:
            prs_from_rfp = frappe.db.sql("""
                SELECT name, custom_refundable
                FROM `tabPurchase Receipt`
                WHERE custom_request_for_purchase = %s
                AND (custom_refundable IS NULL OR custom_refundable = 0)
            """, rfp.name, as_dict=1)
            
            for pr in prs_from_rfp:
                frappe.db.set_value("Purchase Receipt", pr.name, "custom_refundable", 1, update_modified=False)
                pr_updated += 1
                affected_docs['pr'].append({
                    'rfm': rfm.name,
                    'rfp': rfp.name,
                    'po': None,
                    'pr': pr.name,
                    'old_value': pr.custom_refundable or 0,
                    'linked_via': 'custom_request_for_purchase'
                })
    
    frappe.db.commit()
    
    print(f"\nBackfill completed:")
    print(f"- RFPs updated: {rfp_updated}")
    print(f"- Purchase Orders updated: {po_updated}")
    print(f"- Purchase Receipts updated: {pr_updated}")
    


