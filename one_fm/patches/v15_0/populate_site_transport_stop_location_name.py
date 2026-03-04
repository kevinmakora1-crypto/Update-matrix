import frappe

def execute():
	# Populate the new mandatory field 'site_transport_stop_location_name' 
	# with the existing record ID (name) for all records.
	
	frappe.db.sql("""
		UPDATE `tabSite Transport Stop Location`
		SET site_transport_stop_location_name = name
		WHERE site_transport_stop_location_name IS NULL OR site_transport_stop_location_name = ''
	""")
	
	frappe.db.commit()
