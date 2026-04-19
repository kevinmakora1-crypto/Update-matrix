import frappe
from frappe.utils.password import update_password

def execute():
    email = "mobileapp@one-fm.com"
    pwd = "password123"
    
    # 1. Create or get User
    if not frappe.db.exists("User", email):
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": "Mobile",
            "last_name": "App Tester",
            "send_welcome_email": 0
        })
        user.insert(ignore_permissions=True)
        user.add_roles("Employee", "HR Manager") # Giving HR Manager just in case resignation workflow needs it
        update_password(email, pwd)
        print(f"Created User: {email}")
    else:
        update_password(email, pwd)
        print(f"Updated password for existing User: {email}")

    # 2. Add Employee record linked to the User
    emp_name = frappe.db.get_value("Employee", {"user_id": email}, "name")
    if not emp_name:
        emp = frappe.get_doc({
            "doctype": "Employee",
            "first_name": "Mobile",
            "last_name": "App Tester",
            "employee_id": "EMP-APP-TESTER",
            "user_id": email,
            "gender": "Male",
            "status": "Active",
            "date_of_birth": "1990-01-01",
            "date_of_joining": "2020-01-01",
        })
        emp.flags.ignore_mandatory = True
        emp.insert(ignore_permissions=True)
        emp_name = emp.name
        print(f"Created Employee record: {emp_name}")
    else:
        emp = frappe.get_doc("Employee", emp_name)
    
    emp.db_set("employee_id", "EMP-APP-TESTER")
    emp.db_set("enrolled", 1)
    emp.db_set("registered", 1)

    frappe.db.commit()

    print("\n--- CREDENTIALS ---")
    print(f"Employee ID: EMP-APP-TESTER")
    print(f"Password: {pwd}")
    print(f"Email (for desktop auth): {email}")
    print("-------------------")
