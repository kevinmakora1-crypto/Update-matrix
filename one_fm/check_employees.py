import frappe
def run():
    print(f"Checking Busara Juma Suleiman: {frappe.db.get_value('Employee', {'employee_name': 'Busara Juma Suleiman'}, 'name')}")
    print(f"Checking Yam Bahadur Thapa: {frappe.db.get_value('Employee', {'employee_id': '2202025NP191'}, 'name')}")
run()
