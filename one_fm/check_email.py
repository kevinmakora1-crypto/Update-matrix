import frappe

def run():
    accounts = frappe.get_all("Email Account", filters={"enable_outgoing": 1}, fields=["name", "default_outgoing"])
    print(f"Enabled Outgoing Accounts: {accounts}")
    
    frappe.clear_cache()
    print("Cache cleared.")
