import frappe
import logging

logger = logging.getLogger(__name__)

def execute():
	"""
	Check Purchase Orders in KWD for items where:
	1. rate != base_rate
	2. rate != net_rate
	3. rate != base_net_rate
	4. net_amount == base_net_amount
	"""
	results = frappe.db.sql("""
		SELECT
			poi.idx as row_number,
			poi.name as item_name,
			poi.parent,
			poi.item_code,
			poi.rate,
			poi.amount,
			poi.base_rate,
			poi.net_rate,
			poi.base_net_rate,
			poi.net_amount,
			poi.base_net_amount
		FROM 
			`tabPurchase Order Item` poi
		JOIN 
			`tabPurchase Order` po ON poi.parent = po.name
		WHERE 
			po.currency = 'KWD'
			AND poi.rate != poi.base_rate
			AND poi.rate != poi.net_rate
			AND poi.rate != poi.base_net_rate
			
	""", as_dict=True)

	if results:
		logger.info(f"Found {len(results)} Purchase Order Items with rate discrepancies but equal net amounts")
		for row in results:
			try:
				row_doc = frappe.get_doc("Purchase Order Item", row.item_name)
				row_doc.db_set('base_rate', row.rate)
				row_doc.db_set('net_rate', row.rate)
				row_doc.db_set('base_net_rate', row.rate)
				if row_doc.amount != row_doc.net_amount:
					row_doc.db_set('net_amount', row.amount)
					row_doc.db_set('base_net_amount', row.amount)
				frappe.db.commit()
			except Exception:
				frappe.db.rollback()
				frappe.log_error(
					title="Failed to update Purchase Order Item in check_po_kwd_rates patch",
					message=f"Error while updating Purchase Order Item {row.item_name}"
				)
				raise

	else:
		logger.info("No Purchase Order Items found matching the criteria")
