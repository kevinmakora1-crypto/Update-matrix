import frappe
from frappe.utils.password import update_password

def run():
    # 1. Update Administrator
    frappe.db.set_value('User', 'Administrator', 'full_name', 'A')
    update_password('Administrator', '0790846301')
    
    # 2. Detach from any employee
    frappe.db.sql("UPDATE tabEmployee SET user_id=NULL WHERE user_id='Administrator'")
    
    frappe.db.commit()
    print("Administrator updated and detached.")

run()
