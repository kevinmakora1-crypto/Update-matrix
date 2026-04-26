import frappe

def get_credentials():
    employees = frappe.get_all('Employee', fields=['name', 'user_id', 'employee_name'], filters={'user_id': ['!=', '']}, limit=1)

    if not employees:
        # Find an employee without a user, and create a user for them or link them
        employees = frappe.get_all('Employee', fields=['name', 'employee_name'], limit=1)
        if not employees:
            print("No employees found.")
            return
        emp = employees[0]
        email = f"test_{emp.name.replace('-', '_').lower()}@example.com"
        if not frappe.db.exists('User', email):
            user = frappe.get_doc({
                'doctype': 'User',
                'email': email,
                'first_name': emp.employee_name or 'Test',
                'send_welcome_email': 0
            })
            user.flags.ignore_permissions = True
            user.insert()
        
        frappe.db.set_value('Employee', emp.name, 'user_id', email)
        emp_user_id = email
        emp_name = emp.name
    else:
        emp_user_id = employees[0].user_id
        emp_name = employees[0].name

    # Set password
    frappe.utils.password.update_password(emp_user_id, "123456")
    frappe.db.commit()

    print(f"Employee ID: {emp_name}")
    print(f"Password: 123456")
