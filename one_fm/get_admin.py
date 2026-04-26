import frappe
def run():
    user = frappe.get_doc('User', 'Administrator')
    print(f"ADMIN_CREDS:{user.api_key}:{user.get_password('api_secret')}")
run()
