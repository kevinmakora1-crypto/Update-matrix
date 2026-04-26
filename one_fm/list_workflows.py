import frappe
def run():
    workflows = frappe.get_all("Workflow", fields=["name", "document_type", "is_active"])
    print(workflows)
run()
