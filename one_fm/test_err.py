import frappe

def get():
    logs = frappe.get_all('Error Log', fields=['method', 'error', 'creation'], order_by='creation desc', limit=5)
    for log in logs:
        print(f"\n[{log.creation}] [{log.method}]:")
        print(log.error[:2000])
        print("---")
