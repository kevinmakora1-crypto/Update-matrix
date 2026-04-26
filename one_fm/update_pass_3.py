import frappe
from frappe.utils.password import update_password

def run():
    user_id = '2101123gh176@one-fm.com'
    update_password(user_id, '123456')
    frappe.db.commit()
    print(f"Password updated for {user_id} (Employee ID: 2101123GH176)")

run()
