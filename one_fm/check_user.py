import frappe
def run():
    print(frappe.db.get_value('Employee', {'employee_id': '2503003KE199'}, 'user_id'))
run()
