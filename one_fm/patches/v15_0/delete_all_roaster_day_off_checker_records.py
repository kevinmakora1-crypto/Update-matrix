import frappe

def execute():
    frappe.db.sql("""
		DELETE FROM `tabRoster Day Off Checker`	
	""")
    
    frappe.db.sql("""
		DELETE FROM `tabRoster Day Off Detail`
	""")
    
    frappe.db.commit() 