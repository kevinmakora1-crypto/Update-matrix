import frappe
from frappe.desk.form.assign_to import remove
def run():
    try:
        doc = frappe.get_last_doc("Employee Resignation Extension")
        if doc.supervisor:
            print("Supervisor is:", doc.supervisor)
            remove(doc.doctype, doc.name, doc.supervisor)
            print("Removed assignment")
    except Exception as e:
        print("Exception:", e)
