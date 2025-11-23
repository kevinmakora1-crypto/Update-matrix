import frappe

def execute():
    frappe.reload_doctype("Project")
    frappe.reload_doctype("Operations Site")
    frappe.reload_doctype("Operations Shift")
    frappe.reload_doctype("ToDo")
    frappe.reload_doctype("Task")
    frappe.reload_doctype("Request for Material")

    # Mapping of old and new values
    employee_map = {"HR-EMP-00002": "HR-EMP-00001"}
    user_map = {"tctkumar@one-fm.com": "abdullah@one-fm.com"}

    # Update Project doctype
    update_project_doctype(employee_map)

    # Update Operations Site doctype
    update_operations_site_doctype(employee_map)

    # Update Operations Shift doctype
    update_operations_shift_doctype(employee_map)

    # Update ToDo doctype
    update_todo_doctype(user_map)

    # Update Task doctype
    update_task_doctype(user_map)

    # Update Request for Material doctype
    update_request_for_material_doctype(user_map)

def update_project_doctype(employee_map):
    project_filters = {"account_manager": ("IN", list(employee_map.keys()))}
    projects = frappe.get_all("Project", filters=project_filters, fields=["name"])

    for project in projects:
        try:
            doc = frappe.get_doc("Project", project.name)
            doc.account_manager = employee_map.get(doc.account_manager)
            doc.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(message=f"Failed to update Project {project.name}: {e}", title="Patch Update Error")

def update_operations_site_doctype(employee_map):
    site_filters = {"account_supervisor": ("IN", list(employee_map.keys()))}
    sites = frappe.get_all("Operations Site", filters=site_filters, fields=["name"])

    for site in sites:
        try:
            doc = frappe.get_doc("Operations Site", site.name)
            doc.account_supervisor = employee_map.get(doc.account_supervisor)
            doc.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(message=f"Failed to update Operations Site {site.name}: {e}", title="Patch Update Error")

def update_operations_shift_doctype(employee_map):
    shift_names = frappe.get_all("Operations Shift Supervisor", filters={"supervisor": ("IN", list(employee_map.keys()))}, pluck="parent")

    for shift_name in shift_names:
        try:
            doc = frappe.get_doc("Operations Shift", shift_name)
            for row in doc.shift_supervisor:
                if row.supervisor in employee_map:
                    row.supervisor = employee_map[row.supervisor]
            doc.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(message=f"Failed to update Operations Shift {shift_name}: {e}", title="Patch Update Error")


def update_todo_doctype(user_map):
    todo_filters = {"status": "Open", "allocated_to": ("IN", list(user_map.keys()))}
    todos = frappe.get_all("ToDo", filters=todo_filters, fields=["name"])

    for todo in todos:
        try:
            doc = frappe.get_doc("ToDo", todo.name)
            doc.allocated_to = user_map.get(doc.allocated_to)
            doc.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(message=f"Failed to update ToDo {todo.name}: {e}", title="Patch Update Error")

def update_task_doctype(user_map):
    task_assignments = frappe.get_all("Task Assignment", filters={"user": ("IN", list(user_map.keys()))}, pluck="parent")

    tasks = frappe.get_all("Task", filters={"name": ("IN", task_assignments), "status": ("IN", ["Open", "Working", "Overdue"])}, fields=["name"])

    for task in tasks:
        try:
            doc = frappe.get_doc("Task", task.name)
            for user in doc.custom_assigned_to:
                if user.user in user_map:
                    user.user = user_map.get(user.user)
            doc.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(message=f"Failed to update Task {task.name}: {e}", title="Patch Update Error")


def update_request_for_material_doctype(user_map):
    rfm_filters = {
        "docstatus": 0,
        "request_for_material_approver": ("IN", list(user_map.keys())),
    }
    rfms = frappe.get_all("Request for Material", filters=rfm_filters, fields=["name"])

    for rfm in rfms:
        try:
            doc = frappe.get_doc("Request for Material", rfm.name)
            doc.request_for_material_approver = user_map.get(doc.request_for_material_approver)
            doc.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(message=f"Failed to update Request for Material {rfm.name}: {e}", title="Patch Update Error")
