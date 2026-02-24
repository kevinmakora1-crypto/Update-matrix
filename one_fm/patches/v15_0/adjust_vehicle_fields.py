import frappe

def execute():
    frappe.db.set_value("DocField", {"parent": "Vehicle", "fieldname": "employee"}, "reqd", 1)
    frappe.db.set_value("DocField", {"parent": "Vehicle", "fieldname": "location"}, "label", "Vehicle Location")
    frappe.db.set_value("DocField", {"parent": "Vehicle", "fieldname": "location"}, "fieldtype", "Link")
    frappe.db.set_value("DocField", {"parent": "Vehicle", "fieldname": "location"}, "options", "Location")
    frappe.db.set_value("DocField", {"parent": "Vehicle", "fieldname": "location"}, "reqd", 1)
    frappe.clear_cache(doctype="Vehicle")
