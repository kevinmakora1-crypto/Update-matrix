import frappe

def run():
    # 1. Unlink any currently linked employee for Administrator
    current_emp = frappe.db.get_value("Employee", {"user_id": "Administrator"}, "name")
    if current_emp:
        frappe.db.set_value("Employee", current_emp, "user_id", "")
        print(f"Unlinked {current_emp}")
    
    # 2. Find a perfect demo worker employee (Active, has Designation, has Project, has Shift)
    demo_emp = frappe.db.get_value("Employee", {
        "status": "Active",
        "designation": ["!=", ""],
        "project": ["!=", ""]
    }, "name")
    
    if demo_emp:
        # Clear out any user id that might belong to the demo_emp
        frappe.db.set_value("Employee", demo_emp, "user_id", "Administrator")
        frappe.db.commit()
        print(f"✅ Successfully linked Administrator to Demo Worker: {demo_emp}")
        
        # Print details for confirmation
        doc = frappe.get_doc("Employee", demo_emp)
        print(f"Designation: {doc.designation}")
        print(f"Project: {doc.project}")
    else:
        print("Failed to find a perfect demo employee.")
