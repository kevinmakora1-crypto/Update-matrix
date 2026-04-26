import frappe
def run():
    log = frappe.db.get_list('Error Log', fields=['name', 'creation', 'method', 'error'], order_by='creation desc', limit=1)
    if log:
        print(f"NAME: {log[0].name}")
        print(f"CREATED: {log[0].creation}")
        print(f"METHOD: {log[0].method}")
        print(f"ERROR: {log[0].error[:200]}")
run()
