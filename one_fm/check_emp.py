import frappe

def run():
    emp = frappe.db.get_value('Employee', {'employee_id': '2503003KE199'}, ['name', 'project', 'designation'], as_dict=1)
    print(emp)

run()
