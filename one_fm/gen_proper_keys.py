import frappe
from frappe.core.doctype.user.user import generate_keys

def run():
    user = "y.thapa@one-fm.com"
    print(f"Generating proper standard keys for {user}...")
    
    # Generate keys using official Frappe logic
    frappe.db.set_value("User", user, {"api_key": "", "api_secret": ""})
    generate_keys(user)
    frappe.db.commit()
    
    u = frappe.get_doc("User", user)
    secret = u.get_password("api_secret")
    print(f"NEW_CREDS:{u.api_key}:{secret}")

run()
