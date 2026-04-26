import frappe

def run():
    emp = frappe.get_doc('Employee', 'HR-EMP-03519')
    print('EMPLOYEE_ID:', emp.employee_id)
