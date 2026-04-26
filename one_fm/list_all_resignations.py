import frappe
def run():
    resignations = frappe.get_all('Employee Resignation', fields=['name', 'workflow_state', 'owner', 'creation'], limit=10)
    for r in resignations:
        print(r)
run()
