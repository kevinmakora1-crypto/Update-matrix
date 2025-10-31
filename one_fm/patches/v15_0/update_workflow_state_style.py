import frappe

def execute():
	if not frappe.db.exists("Property Setter", "Workflow State-style-reqd"):
		frappe.get_doc({
			"doctype": "Property Setter",
			"doctype_or_field": "DocField",
			"doc_type": "Workflow State",
			"field_name": "style",
			"property": "reqd",
			"property_type": "Check",
			"value": "1"
		}).insert(ignore_permissions=True)
		frappe.db.commit()
