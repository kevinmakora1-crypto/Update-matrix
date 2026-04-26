import frappe

def get_latest_errors():
    errors = frappe.get_all("Error Log", 
        fields=["name", "method", "error", "creation", "owner"], 
        order_by="creation desc", 
        limit=3
    )
    for err in errors:
        print(f"--- ERROR START: {err.name} ---")
        print(f"Timestamp: {err.creation}")
        print(f"Method: {err.method}")
        print(f"Owner: {err.owner}")
        print(f"Error Content:\n{err.error}")
        print(f"--- ERROR END: {err.name} ---")

if __name__ == "__main__":
    get_latest_errors()
