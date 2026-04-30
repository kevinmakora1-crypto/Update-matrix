import frappe

def execute():
    email = "mobileapp@one-fm.com"
    
    # 1. Ensure the user's "User App Service" has all available apps
    # Fetch all App Services available universally
    all_services = frappe.get_all("App Service", fields=["name"])
    
    # Check if a User App Service exists for this user profile
    existing = frappe.db.exists("User App Service", {"user": email})
    
    if existing:
        doc = frappe.get_doc("User App Service", existing)
        doc.set("service_detail", [])
        for svc in all_services:
            doc.append("service_detail", {
                "service": svc["name"]
            })
        doc.save(ignore_permissions=True)
        print("Updated existing User App Service permissions to include everything.")
    else:
        emp_name = frappe.db.get_value("Employee", {"user_id": email}, "name")
        doc = frappe.get_doc({
            "doctype": "User App Service",
            "employee": emp_name,
            "user": email,
            "service_detail": [{"service": svc["name"]} for svc in all_services]
        })
        doc.insert(ignore_permissions=True)
        print("Created new User App Service configuration with all services enabled.")
        
    frappe.db.commit()
