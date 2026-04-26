import frappe
def run():
    errors = frappe.get_all('Error Log', filters={'error': ['like', '%Missing Resignation Letter%']}, fields=['name', 'creation', 'owner'])
    print(errors)
run()
