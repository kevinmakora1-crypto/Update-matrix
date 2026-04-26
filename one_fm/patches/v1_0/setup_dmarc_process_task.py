import frappe

def execute():
	"""Create the Method and Process Task records for automated DMARC report fetching."""

	method_path = "one_fm.developer.dmarc_processor.fetch_and_process_dmarc_reports"

	# Step 1: Create Method record if it doesn't exist
	if not frappe.db.exists("Method", method_path):
		if frappe.db.exists("DocType", "Method"):
			frappe.get_doc({
				"doctype": "Method",
				"method": method_path,
				"document_type": "DMARC Report",
				"description": "Automated fetching of DMARC aggregate reports via IMAP"
			}).insert(ignore_permissions=True)
			frappe.db.commit()

	# Step 2: Check if a Process Task already exists for this method
	if frappe.db.exists("DocType", "Process Task"):
		existing = frappe.db.exists("Process Task", {"method": method_path})
		if not existing:
			# We need a Process and Task Type to create a Process Task
			# Skip if these don't exist yet (admin will set up manually)
			if not frappe.db.exists("DocType", "Task Type"):
				return

			task_type = frappe.db.get_value("Task Type", {"is_routine_task": 1}, "name")
			if not task_type:
				# Use any available task type
				task_type = frappe.db.get_value("Task Type", {}, "name")

			if not task_type:
				return

			try:
				frappe.get_doc({
					"doctype": "Process Task",
					"task": "Daily DMARC Report Fetching",
					"task_type": task_type,
					"frequency": "Daily",
					"is_automated": 1,
					"is_erp_task": 1,
					"is_active": 1,
					"method": method_path,
					"coordination_needed": "No",
					"start_date": frappe.utils.today()
				}).insert(ignore_permissions=True)
				frappe.db.commit()
			except Exception:
				# Process field is mandatory but we don't know which Process to use
				# Log and let admin configure manually
				frappe.log_error(
					"DMARC Process Task could not be auto-created. "
					"Please create it manually in Process Task list.",
					"DMARC Setup Patch"
				)
