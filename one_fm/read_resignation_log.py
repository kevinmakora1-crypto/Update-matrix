import frappe
def run():
    log = frappe.db.get_list('Error Log', filters={'method': ['like', '%resignation%']}, fields=['method', 'error'], order_by='creation desc', limit=1)
    if log:
        print(f"METHOD: {log[0].method}")
        print(f"ERROR: {log[0].error}")
    else:
        print("No resignation logs found.")
run()
