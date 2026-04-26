import frappe

def run():
    logs = frappe.get_all("Error Log", limit=5, order_by="creation desc", fields=["error", "method", "creation"])
    for l in logs:
        print(f"[{l.creation}] {l.method}")
        print(l.error[:500])
        print("-" * 50)

if __name__ == "__main__":
    frappe.connect()
    run()
