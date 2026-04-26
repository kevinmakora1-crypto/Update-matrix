import frappe
def run():
    frappe.db.set_value('User', 'y.thapa@one-fm.com', 'api_secret', 'secret123')
    frappe.db.commit()
    print("API_SECRET_SET_SUCCESS")
run()
