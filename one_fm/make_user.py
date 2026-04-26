import frappe

def run():
    emp = frappe.get_doc("Employee", "HR-EMP-03519")
    user_email = f"emp{emp.employee.lower()}@one-fm.com"
    if not frappe.db.exists("User", user_email):
        u = frappe.new_doc("User")
        u.email = user_email
        u.first_name = emp.employee_name or emp.first_name
        u.send_welcome_email = 0
        u.insert(ignore_permissions=True)
    frappe.db.set_value("Employee", emp.name, "user_id", user_email)
    frappe.utils.password.update_password(user_email, "Password@123")
    frappe.db.commit()
    print("Success! Created user and mapped!")
