import frappe
def run():
    log = frappe.db.get_list('Error Log', filters={'method': ['like', '%resignation%']}, fields=['error'], order_by='creation desc', limit=1)
    if log:
        lines = log[0].error.split("\n")
        # Print lines that look like file paths in our app
        for line in lines:
            if "apps/one_fm" in line:
                print(line.strip())
run()
