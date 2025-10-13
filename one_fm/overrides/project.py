import frappe
from frappe.core.doctype.version.version import get_diff
from frappe.desk.form.assign_to import add as assign, DuplicateToDoError, remove as remove_assignment
from frappe import _

def update_project_user_assignment(doc, method):
    last_doc = doc.get_doc_before_save()
    
    if not last_doc: #new document
        assign_users_to_project(doc)
    else:
        added_users, removed_users = get_changed_users(doc)
        if added_users:
            for user in added_users:
                add_assignment(user, doc.name)
        if removed_users:
            for user in removed_users:
                remove_assignment("Project", doc.name, user)

def assign_users_to_project(doc):
    for user in doc.users:
        add_assignment(user.user, doc.name)
    add_assignment(doc.project_manager, doc.name)

def add_assignment(user, project):
    try:
        assign({
            "doctype": "Project",
            "name": project,
            "assign_to": [user],
            "description": _("The project is assigned")
        })
    except DuplicateToDoError:
        frappe.message_log.pop()
        pass

def get_changed_users(project):
    project_before_save = project.get_doc_before_save()
    if project_before_save is None:
        return [], []
    changes = get_diff(project_before_save, project, for_child=True)

    user_change = next((c for c in changes.changed if c[0] == "users"), None)
    if not user_change:
        return [], []

    old_value, new_value = user_change[1], user_change[2]
    old_users = [user.user for user in old_value]
    new_users = [user.user for user in new_value]

    added_users = list(set(new_users) - set(old_users))
    removed_users = list(set(old_users) - set(new_users))

    return added_users, removed_users
