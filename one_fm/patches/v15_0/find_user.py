import frappe

def execute():
    email = "mobileapp@one-fm.com"
    pwd = "password123"

    # Find the first real, active Employee who has a department and designation
    emps = frappe.get_list("Employee", 
        filters={"status": "Active", "name": ["!=", "HR-EMP-00040"]}, 
        fields=["name", "employee_name", "employee_id", "department", "designation"], 
        limit=1
    )
    
    if not emps:
        print("No real employees found in local DB besides the test one.")
        return

    real_emp = emps[0]
    emp_doc = frappe.get_doc("Employee", real_emp.name)
    
    # Force this real employee to be our test user
    emp_doc.db_set("user_id", email)
    emp_doc.db_set("enrolled", 1)
    emp_doc.db_set("registered", 1)
    
    # Remove user_id from the old dummy tester so we don't have duplicates
    dummy = frappe.get_list("Employee", filters={"name": "HR-EMP-00040"})
    if dummy:
        frappe.db.set_value("Employee", "HR-EMP-00040", "user_id", None)
        
    # Also assign all App Services to this real employee so the home screen works
    frappe.db.delete("User App Service", {"user": email})
    all_services = frappe.get_all("App Service", fields=["name"])
    uas = frappe.get_doc({
        "doctype": "User App Service",
        "employee": emp_doc.name,
        "user": email,
        "service_detail": [{"service": svc["name"]} for svc in all_services]
    })
    uas.insert(ignore_permissions=True)
    
    frappe.db.commit()

    print("\n--- NEW CREDENTIALS ---")
    print(f"Employee ID: {emp_doc.employee_id}")
    print(f"Employee Name: {emp_doc.employee_name}")
    print(f"Department: {emp_doc.department}")
    print(f"Designation: {emp_doc.designation}")
    print(f"Password: {pwd}")
    print("-----------------------")

