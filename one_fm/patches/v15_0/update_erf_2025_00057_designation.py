import frappe

def execute():
	if frappe.db.exists("ERF", "ERF-2025-00057"):
		frappe.db.set_value("ERF", "ERF-2025-00057", "designation", "Security Guard")
