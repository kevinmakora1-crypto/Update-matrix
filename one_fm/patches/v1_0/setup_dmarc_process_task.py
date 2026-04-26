import frappe

def execute():
	"""Create the Method and Process Task records for automated DMARC report fetching."""

	method_path = "one_fm.developer.dmarc_processor.fetch_and_process_dmarc_reports"

	# Step 1: Create Method record if it doesn't exist
	if frappe.db.exists("DocType", "Method") and not frappe.db.exists("Method", method_path):
		frappe.get_doc({
			"doctype": "Method",
			"method": method_path,
			"document_type": "DMARC Report",
			"description": "Automated fetching of DMARC aggregate reports via IMAP"
		}).insert(ignore_permissions=True)
		frappe.db.commit()

	# Step 2: Create Process Task if it doesn't exist
	if not frappe.db.exists("DocType", "Process Task"):
		return

	# Check if a Process Task already exists for this method
	existing = frappe.db.exists("Process Task", {"method": method_path})
	if existing:
		return

	try:
		doc = frappe.get_doc({
			"doctype": "Process Task",
			"process_name": "Others",
			"task": "Daily DMARC Report Fetching",
			"task_type": "Routine",
			"frequency": "Daily",
			"hours_per_frequency": 0.5,
			"is_erp_task": 1,
			"is_automated": 1,
			"is_active": 1,
			"is_routine_task": 1,
			"method": method_path,
			"coordination_needed": "No",
			"start_date": frappe.utils.today()
		})
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		frappe.logger().info(f"DMARC Process Task created: {doc.name}")
	except Exception as e:
		frappe.log_error(
			f"DMARC Process Task could not be auto-created: {str(e)}",
			"DMARC Setup Patch"
		)
