import frappe
def run():
    user = "y.thapa@one-fm.com"
    frappe.db.set_value("User", user, "api_key", "key12345")
    # Setting api_secret via SQL to avoid any encryption logic that might be failing
    frappe.db.sql(f"UPDATE `tabUser` SET api_secret='secret12345' WHERE name='{user}'")
    frappe.db.commit()
    print("FINAL_FIX_SUCCESS")
run()
