import frappe
def run():
    print(frappe.db.get_value('Employee', 'HR-EMP-03519', ['name', 'user_id', 'employee_id'], as_dict=1))
run()
