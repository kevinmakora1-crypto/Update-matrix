import frappe
def run():
    emp = frappe.get_doc("Employee", "HR-EMP-03519")
    if emp.user_id:
        frappe.utils.password.update_password(emp.user_id, "Password@123")
        frappe.db.commit()
        print(f"ID is {emp.employee}")
        print(f"Password reset to Password@123")
