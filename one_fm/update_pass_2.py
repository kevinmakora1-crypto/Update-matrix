import frappe
from frappe.utils.password import update_password

def run():
    user_id = 'y.thapa@one-fm.com'
    update_password(user_id, '123456')
    frappe.db.commit()
    print(f"Password updated for {user_id} (Employee ID: 2202025NP191)")

run()
