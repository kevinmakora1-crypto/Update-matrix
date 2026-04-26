import frappe

def run():
    user = "y.thapa@one-fm.com"
    print(f"Properly setting API Secret for {user}...")
    # Use the official method to set encrypted password/secret
    frappe.utils.password.update_password(user, 'secret123', doctype='User', fieldname='api_secret')
    frappe.db.commit()
    print("SUCCESS: API Secret encrypted and saved.")

run()
