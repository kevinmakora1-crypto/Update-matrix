import frappe
def run():
    employees = frappe.get_list('Employee', filters={'status': 'Active', 'user_id': ['!=', '']}, fields=['name', 'employee_id', 'user_id'], limit=5)
    print(employees)
run()
