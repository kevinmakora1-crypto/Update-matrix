import frappe

def run():
    doc = frappe.get_doc("Workflow", "Employee Resignation")
    
    # Update existing transition condition
    for t in doc.transitions:
        if t.action == "Accept and Forward to OM":
            t.condition = 'frappe.db.get_value("Employee", doc.employee, "site") or frappe.db.get_value("Employee", doc.employee, "shift")'

    # Check if the corporate transition already exists
    exists = any(t.action == "Approve" and t.state == "Pending Supervisor" for t in doc.transitions)
    
    if not exists:
        doc.append("transitions", {
            "state": "Pending Supervisor",
            "action": "Approve",
            "next_state": "Approved",
            "allowed": "System Manager",
            "allowed_user_field": "supervisor",
            "condition": 'not frappe.db.get_value("Employee", doc.employee, "site") and not frappe.db.get_value("Employee", doc.employee, "shift")'
        })
        doc.save()
        frappe.db.commit()
        print("Workflow patched successfully!")
    else:
        doc.save()
        frappe.db.commit()
        print("Workflow already contained the rule. Conditions updated!")

    # Patch Extension Workflow
    ext_wf = frappe.get_doc("Workflow", "Employee Resignation Extension Workflow")
    for t in ext_wf.transitions:
        if t.action == "Accept":
            t.condition = 'frappe.db.get_value("Employee Resignation", doc.employee_resignation, "project_allocation") != "ONE FM - Head Office"'
    exists = any(t.action == "Approve" and t.state == "Pending Supervisor" for t in ext_wf.transitions)
    if not exists:
        ext_wf.append("transitions", {
            "state": "Pending Supervisor",
            "action": "Approve",
            "next_state": "Approved",
            "allowed": "Employee",
            "condition": 'frappe.db.get_value("Employee Resignation", doc.employee_resignation, "project_allocation") == "ONE FM - Head Office"'
        })
    ext_wf.save()

    # Patch Withdrawal Workflow
    wdl_wf = frappe.get_doc("Workflow", "Employee Resignation Withdrawal")
    for t in wdl_wf.transitions:
        if t.action == "Accept":
            t.condition = 'frappe.db.get_value("Employee Resignation", doc.employee_resignation, "project_allocation") != "ONE FM - Head Office"'
    exists = any(t.action == "Approve" and t.state == "Pending Supervisor" for t in wdl_wf.transitions)
    if not exists:
        wdl_wf.append("transitions", {
            "state": "Pending Supervisor",
            "action": "Approve",
            "next_state": "Approved",
            "allowed": "Employee",
            "condition": 'frappe.db.get_value("Employee Resignation", doc.employee_resignation, "project_allocation") == "ONE FM - Head Office"'
        })
    wdl_wf.save()
    frappe.db.commit()
    print("Extension and Withdrawal Workflows patched successfully!")
