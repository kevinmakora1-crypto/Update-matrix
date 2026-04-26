import frappe
def run():
    print(f"BUSARA: {frappe.get_all('Employee', filters={'employee_name': 'Busara Juma Suleiman'}, fields=['name', 'employee_id', 'user_id'])}")
    print(f"YAM: {frappe.get_all('Employee', filters={'employee_id': '2202025NP191'}, fields=['name', 'employee_name', 'user_id'])}")
run()
