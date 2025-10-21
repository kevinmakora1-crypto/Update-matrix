import frappe

def execute():
	"""Patch: Update submitted RFPs stuck in 'Pending Approval' to 'Approved'.
	Idempotent: safe to re-run (only affects matching state).
	"""
	# Fetch targeted RFPs (docstatus=1 ensures submitted)
	rfps = frappe.db.get_list(
		"Request for Purchase",
		filters={"docstatus": 1, "workflow_state": "Pending Approval"},
		pluck="name"
	)
	if not rfps:
		return

	updated = 0
	for name in rfps:
		try:
			# Direct field update; ignore permissions per requirements
			frappe.db.set_value(
				"Request for Purchase",
				name,
				{"workflow_state": "Approved", "status": "Approved"},
				update_modified=True
			)
			updated += 1
		except Exception as e:
			frappe.log_error(f"Failed updating RFP {name}: {e}", "Patch update_rfp_records")

	rejected_rfp = rfps = frappe.db.get_list(
		"Request for Purchase",
		filters={"workflow_state": "Rejected"},
		pluck="name"
	)
	if not rejected_rfp:
		return
	for name in rejected_rfp:
		try:
			# Direct field update; ignore permissions per requirements
			frappe.db.set_value(
				"Request for Purchase",
				name,
				{"status": "Rejected"},
				update_modified=True
			)
		except Exception as e:
			frappe.log_error(f"Failed updating RFP {name}: {e}", "Patch update_rfp_records")
    
 
 
    
	frappe.db.commit()

	