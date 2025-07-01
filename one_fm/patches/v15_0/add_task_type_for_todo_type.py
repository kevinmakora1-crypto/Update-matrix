import frappe

def execute():
    task_types = ["Routine", "Action", "Project"]
    for task_type in task_types:
        doc = frappe.new_doc("Task Type")
        doc.__newname = task_type
        doc.insert(ignore_permissions=True)
