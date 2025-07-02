import frappe

def execute():
    task_types = ["Routine", "Action", "Project"]
    for task_type in task_types:
        if not frappe.db.exists("Task Type", task_type):
            doc = frappe.new_doc("Task Type")
            doc.__newname = task_type
            doc.insert(ignore_permissions=True)
