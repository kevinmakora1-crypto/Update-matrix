import frappe

def fix_db():
    frappe.db.sql('UPDATE tabDocType SET custom=1, module="One Fm" WHERE name="Employee Resignation Extension"')
    frappe.db.commit()
    frappe.clear_cache(doctype='Employee Resignation Extension')
