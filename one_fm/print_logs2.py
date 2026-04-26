import frappe

def execute():
    logs = frappe.get_all("Error Log", fields=["method", "creation"], limit=5, order_by="creation desc")
    for log in logs:
        print(f"Time: {log.creation} | Method: {log.method}")
