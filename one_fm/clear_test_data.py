import frappe

def run():
    doctypes = [
        "Employee Resignation Extension",
        "Employee Resignation Withdrawal",
        "Employee Resignation",
        "Employee Resignation Extension Item",
        "Employee Resignation Withdrawal Item",
        "Employee Resignation Item"
    ]
    
    for dt in doctypes:
        print(f"Clearing {dt}...")
        frappe.db.sql(f"DELETE FROM `tab{dt}`")
        # Also clear child tables if any are not in the list
        
    # Clear ToDos related to these doctypes
    print("Clearing related ToDos...")
    frappe.db.sql("""
        DELETE FROM `tabToDo` 
        WHERE reference_type IN ('Employee Resignation', 'Employee Resignation Extension', 'Employee Resignation Withdrawal')
    """)
    
    # Clear Communication/Emails related to these
    print("Clearing related Communications...")
    frappe.db.sql("""
        DELETE FROM `tabCommunication` 
        WHERE reference_doctype IN ('Employee Resignation', 'Employee Resignation Extension', 'Employee Resignation Withdrawal')
    """)

    frappe.db.commit()
    print("All test data cleared successfully.")

