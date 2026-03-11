import frappe

def execute():
	# Populate the new mandatory field 'site_transport_stop_location_name' 
	# with the existing record ID (name) for all records.

	# Reload the DocType to ensure the column exists before running the UPDATE
	frappe.reload_doc("operations", "doctype", "site_transport_stop_location")

	if not frappe.db.has_column("Site Transport Stop Location", "site_transport_stop_location_name"):
		return

	frappe.db.sql("""
		UPDATE `tabSite Transport Stop Location`
		SET site_transport_stop_location_name = name
		WHERE site_transport_stop_location_name IS NULL OR site_transport_stop_location_name = ''
	""")
