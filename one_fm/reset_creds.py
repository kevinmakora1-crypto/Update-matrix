import frappe

def run():
    user = "y.thapa@one-fm.com"
    print(f"Setting fresh API Key and Secret for {user}...")
    
    # Set API Key
    frappe.db.set_value("User", user, "api_key", "thapa_key")
    
    # Set API Secret properly
    frappe.utils.password.update_password(user, "thapa_secret", doctype="User", fieldname="api_secret")
    
    frappe.db.commit()
    print("SUCCESS: Fresh credentials set.")

run()
