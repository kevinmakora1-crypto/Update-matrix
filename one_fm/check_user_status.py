import frappe
def run():
    user = frappe.get_doc('User', 'y.thapa@one-fm.com')
    print(f"User: {user.name}, Enabled: {user.enabled}")
run()
