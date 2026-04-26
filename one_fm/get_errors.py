import frappe

def get_latest_errors():
    errors = frappe.get_all("Error Log", 
        fields=["name", "method", "error", "creation", "owner"], 
        order_by="creation desc", 
        limit=5
    )
    for err in errors:
        print(f"Name: {err.name}")
        print(f"Timestamp: {err.creation}")
        print(f"Method: {err.method}")
        print(f"Owner: {err.owner}")
        print(f"Error: {err.error[:1000]}...")
        print("-" * 80)

if __name__ == "__main__":
    get_latest_errors()
