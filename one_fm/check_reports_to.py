import frappe
def run():
    print(frappe.db.get_value('Employee', 'HR-EMP-03519', 'reports_to'))
run()
