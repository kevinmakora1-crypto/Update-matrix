import frappe

def execute():
    emp = frappe.get_doc("Employee", "HR-EMP-03519")
    print(emp.name, emp.employee_id)
