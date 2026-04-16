import frappe
from frappe import _
import json

@frappe.whitelist(allow_guest=False)
def create_resignation(data=None, employee_id=None, supervisor=None, attachment=None):
    # CapacitorHttp sends flat form params; also support JSON-encoded 'data' string
    if data:
        if isinstance(data, str):
            data = json.loads(data)
        employee_id = data.get('employee_id') or employee_id
        supervisor = data.get('supervisor') or supervisor
        attachment = data.get('attachment') or attachment
    
    if isinstance(attachment, str):
        try:
            attachment = json.loads(attachment)
        except Exception:
            pass
    
    doc = frappe.new_doc("Employee Resignation")
    
    # Do not set doc.date since the field does not exist
    if supervisor:
        doc.supervisor = supervisor
        
    emp_data = frappe.db.get_value("Employee", employee_id, ["employee_name", "first_name", "designation", "project"], as_dict=True) or {}
    
    doc.append("employees", {
        "employee": employee_id,
        "employee_name": emp_data.get("employee_name") or emp_data.get("first_name"),
        "designation": emp_data.get("designation"),
        "project_allocation": emp_data.get("project")
    })
    
    if emp_data.get("project"):
        doc.project_allocation = emp_data.get("project")
    if emp_data.get("designation"):
        doc.designation = emp_data.get("designation")
    
    # Override workflow state manually to bypass strict attachment validations on creation
    doc.workflow_state = "Draft"
    doc.insert(ignore_permissions=True)
    
    if attachment:
        handle_attachment(doc, attachment)
        
    # Explicitly move to Pending Supervisor so it triggers notification securely
    doc.db_set("workflow_state", "Pending Supervisor")
    
    # Manually explicitly ASSIGN the supervisor to trigger Bell/Email Notification
    if supervisor:
        from frappe.desk.form.assign_to import add as add_assign
        add_assign({
            "assign_to": [supervisor],
            "doctype": doc.doctype,
            "name": doc.name,
            "description": frappe._("Review Employee Resignation Request")
        })
        
    return doc.name

@frappe.whitelist(allow_guest=False)
def withdraw_resignation(data=None, employee_id=None, supervisor=None, 
                         employee_resignation=None, reason=None, attachment=None):
    if data:
        if isinstance(data, str):
            data = json.loads(data)
        employee_id = data.get('employee_id') or employee_id
        supervisor = data.get('supervisor') or supervisor
        employee_resignation = data.get('employee_resignation') or employee_resignation
        reason = data.get('reason') or reason
        attachment = data.get('attachment') or attachment

    if isinstance(attachment, str):
        try:
            attachment = json.loads(attachment)
        except Exception:
            pass
    
    if not employee_resignation:
        employee_resignation = frappe.db.get_value(
            "Employee Resignation Item",
            {"employee": employee_id, "parenttype": "Employee Resignation", "docstatus": 1},
            "parent"
        )
        if not employee_resignation:
            frappe.throw(_("No active resignation document found to withdraw."))

    doc = frappe.new_doc("Employee Resignation Withdrawal")
    doc.employee_resignation = employee_resignation
    
    if supervisor:
        doc.supervisor = supervisor
        
    emp_data = frappe.db.get_value("Employee", employee_id, ["employee_name", "first_name", "designation", "project"], as_dict=True) or {}
    
    doc.append("employees", {
        "employee": employee_id,
        "reason": reason,
        "employee_name": emp_data.get("employee_name") or emp_data.get("first_name"),
        "designation": emp_data.get("designation"),
        "project_allocation": emp_data.get("project")
    })
    
    doc.workflow_state = "Draft"
    doc.insert(ignore_permissions=True)
    
    if attachment:
        handle_attachment(doc, attachment)
        
    doc.db_set("workflow_state", "Pending Supervisor")
    
    if supervisor:
        from frappe.desk.form.assign_to import add as add_assign
        add_assign({
            "assign_to": [supervisor],
            "doctype": doc.doctype,
            "name": doc.name,
            "description": frappe._("Review Resignation Withdrawal Request")
        })
        
    return doc.name

def handle_attachment(doc, attachment_data):
    import base64
    from frappe.utils.file_manager import save_file
    
    if isinstance(attachment_data, str):
        attachment_data = json.loads(attachment_data)
        
    file_name = attachment_data.get('attachment_name')
    file_base64 = attachment_data.get('attachment')
    
    if file_name and file_base64:
        content = base64.b64decode(file_base64)
        saved_file = save_file(
            fname=file_name,
            content=content,
            dt=doc.doctype,
            dn=doc.name,
            is_private=1,
            folder="Home/Attachments"
        )
        
        # Link to the row specifically
        if doc.get("employees"):
            row = doc.employees[0]
            if doc.doctype == "Employee Resignation Withdrawal":
                frappe.db.set_value(row.doctype, row.name, "withdrawal_letter", saved_file.file_url)
            else:
                frappe.db.set_value(row.doctype, row.name, "resignation_letter", saved_file.file_url)

@frappe.whitelist(allow_guest=False)
def get_supervisor_dropdown():
    # Return available users to act as supervisor
    return frappe.get_all("User", filters={"enabled": 1, "user_type": "System User"}, fields=["name", "full_name"])
