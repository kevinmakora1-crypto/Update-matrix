import frappe

def execute():
    logs = frappe.get_all("Error Log", fields=["method", "error"], limit=3, order_by="creation desc")
    for log in logs:
        print(f"Method: {log.method}")
        print(f"Error: {log.error}")
        print("-" * 50)
