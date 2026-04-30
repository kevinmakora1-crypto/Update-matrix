import frappe
import json

def check_mobile_config():
    frappe.connect()
    try:
        # 1. Create Service Group if not exists
        group_name = "Resignation"
        if not frappe.db.exists("App Service Group", group_name):
            frappe.get_doc({
                "doctype": "App Service Group",
                "group_name": group_name,
                "icon": "logout",
                "status": "Active"
            }).insert(ignore_permissions=True)
            print(f"Created group: {group_name}")


            
        # 2. Create Services
        new_services = [
            {"service": "Employee Resignation", "icon": "logout", "status": "Active", "group": group_name},
            {"service": "Resignation Withdrawal", "icon": "history", "status": "Active", "group": group_name}
        ]
        
        for s in new_services:
            if not frappe.db.exists("App Service", s["service"]):
                doc = frappe.get_doc({
                    "doctype": "App Service",
                    "service": s["service"],
                    "icon": s["icon"],
                    "status": s["status"],
                    "service_group": s["group"]
                })
                doc.insert(ignore_permissions=True)
                print(f"Created service: {s['service']}")
            else:
                frappe.db.set_value("App Service", s["service"], "status", "Active")
                frappe.db.set_value("App Service", s["service"], "service_group", s["group"])
                print(f"Activated/Updated service: {s['service']}")
                
        frappe.db.commit()
        
        # 3. Update User App Service for Administrator
        all_services = frappe.get_all("App Service", filters={"status": "Active"}, fields=["name"])
        uas_name = frappe.db.get_value("User App Service", {"user": "Administrator"}, "name")
        if uas_name:
            doc = frappe.get_doc("User App Service", uas_name)
            doc.service_detail = []
            for svc in all_services:
                doc.append("service_detail", {"service": svc["name"]})
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            print("Updated User App Service for Administrator")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        frappe.destroy()







if __name__ == "__main__":
    check_mobile_config()
