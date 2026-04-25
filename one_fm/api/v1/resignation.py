import frappe
import json
import re
import base64
from frappe import _
from urllib.parse import unquote
from frappe.utils.file_manager import save_file

def get_request_data(data=None, **kwargs):
    """
    Parses the raw HTTP request body to extract parameters.
    Always runs — does not rely on Frappe's form_dict parsing.
    """
    payload = {}

    # 1. Always try to parse raw body first (works with token auth)
    if hasattr(frappe, 'request'):
        try:
            body = frappe.request.get_data(as_text=True)
            if body:
                # Try JSON first
                try:
                    parsed = json.loads(body)
                    if isinstance(parsed, dict):
                        payload.update(parsed)
                except Exception:
                    # Try URL-encoded (key=val&key2=val2)
                    from urllib.parse import parse_qs
                    parsed_qs = parse_qs(body, keep_blank_values=True)
                    for k, v in parsed_qs.items():
                        payload[k] = v[0] if len(v) == 1 else v
        except Exception:
            pass

    # 2. Override with Frappe form_dict if it has data (cookie-auth path)
    for key in ['employee_id', 'supervisor', 'resignation_initiation_date', 'relieving_date', 'attachment']:
        if not payload.get(key) and frappe.form_dict.get(key):
            payload[key] = frappe.form_dict.get(key)

    # 3. Override with explicit kwargs (highest priority)
    for k, v in kwargs.items():
        if v is not None and k not in ('cmd',):
            payload[k] = v

    # 4. Handle nested 'data' param
    raw_data = data or payload.get('data')
    if raw_data and isinstance(raw_data, str):
        try:
            parsed = json.loads(raw_data)
            if isinstance(parsed, dict):
                payload.update({k: v for k, v in parsed.items() if k not in payload or payload[k] is None})
        except Exception:
            pass
    elif raw_data and isinstance(raw_data, dict):
        payload.update({k: v for k, v in raw_data.items() if k not in payload or payload[k] is None})

    return payload


def resolve_employee_name(employee_id):
    """Resolves custom employee_id to Frappe name (PK)."""
    if not employee_id:
        return None
    # 1. Try by custom field 'employee_id'
    name = frappe.db.get_value("Employee", {"employee_id": employee_id}, "name")
    if name:
        return name
    # 2. Try by PK directly
    if frappe.db.exists("Employee", employee_id):
        return employee_id
    return None

@frappe.whitelist()
def create_resignation(
    employee_id=None,
    supervisor=None,
    resignation_initiation_date=None,
    relieving_date=None,
    attachment=None,
    data=None,
    **kwargs
):
    try:
        # Debug Logging
        raw_body = frappe.request.get_data(as_text=True) if hasattr(frappe, 'request') else "N/A"
        frappe.log_error(title="Resignation API Call", message=f"employee_id={employee_id} supervisor={supervisor} dates={resignation_initiation_date}->{relieving_date}\nRaw Body: {raw_body}")

        # Use explicit params first, fallback to payload extraction
        input_id = employee_id
        if not input_id:
            payload = get_request_data(data, **kwargs)
            input_id = payload.get('employee_id')
            supervisor = supervisor or payload.get('supervisor')
            resignation_initiation_date = resignation_initiation_date or payload.get('resignation_initiation_date')
            relieving_date = relieving_date or payload.get('relieving_date') or payload.get('resignation_date')
            attachment = attachment or payload.get('attachment')

        # Resolve PK
        employee_name = resolve_employee_name(input_id)
        if not employee_name:
            frappe.throw(f"Employee {input_id} not found", frappe.ValidationError)

        # Get employee metadata
        emp_data = frappe.db.get_value("Employee", employee_name, 
            ["employee_name", "designation", "project", "department", "employment_type"], as_dict=True) or {}

        # Create Doc
        doc = frappe.new_doc("Employee Resignation")
        doc.resignation_initiation_date = resignation_initiation_date
        doc.relieving_date = relieving_date
        doc.supervisor = supervisor
        doc.department = emp_data.get("department")
        doc.employment_type = emp_data.get("employment_type")
        doc.project_allocation = emp_data.get("project")
        doc.designation = emp_data.get("designation")
        doc.workflow_state = "Draft"

        # Add to Child Table
        item = doc.append("employees", {
            "employee": employee_name,
            "employee_name": emp_data.get("employee_name"),
            "designation": emp_data.get("designation"),
            "project_allocation": emp_data.get("project"),
            "employment_type": emp_data.get("employment_type"),
            "resignation_letter_date": resignation_initiation_date
        })

        # Save Attachment
        if attachment:
            if isinstance(attachment, str):
                try: attachment = json.loads(attachment)
                except: pass
            
            if isinstance(attachment, dict) and attachment.get('attachment'):
                try:
                    file_content = base64.b64decode(attachment.get('attachment'))
                    file_name = attachment.get('attachment_name') or f"resignation_{input_id}.png"
                    file_doc = save_file(file_name, file_content, "Employee Resignation", "Temporary", is_private=1)
                    item.resignation_letter = file_doc.file_url
                except Exception as e:
                    frappe.log_error("Attachment Error", str(e))

        doc.insert(ignore_permissions=True)
        doc.db_set("workflow_state", "Pending Supervisor")
        
        if supervisor:
            from frappe.desk.form.assign_to import add as add_assign
            try:
                add_assign({
                    "assign_to": [supervisor],
                    "doctype": doc.doctype,
                    "name": doc.name,
                    "description": "Review Employee Resignation Request"
                })
            except: pass

        return {
            "status": "success",
            "message": "Resignation submitted successfully",
            "name": doc.name
        }

    except Exception as e:
        frappe.log_error("Resignation Creation Error", frappe.get_traceback())
        frappe.throw(str(e), frappe.ValidationError)

@frappe.whitelist()
def withdraw_resignation(data=None, **kwargs):
    try:
        payload = get_request_data(data, **kwargs)
        input_id = payload.get('employee_id')
        supervisor = payload.get('supervisor')
        resignation_name = payload.get('employee_resignation')
        reason = payload.get('reason')
        attachment = payload.get('attachment')

        employee_name = resolve_employee_name(input_id)
        if not employee_name:
            frappe.throw(f"Employee {input_id} not found", frappe.ValidationError)

        if not resignation_name:
            resignation_name = frappe.db.get_value("Employee Resignation Item", 
                {"employee": employee_name, "parenttype": "Employee Resignation", "docstatus": 1}, "parent")
            if not resignation_name:
                frappe.throw("No active resignation found to withdraw", frappe.ValidationError)

        emp_data = frappe.db.get_value("Employee", employee_name, ["employee_name", "designation", "project"], as_dict=True) or {}

        doc = frappe.new_doc("Employee Resignation Withdrawal")
        doc.employee_resignation = resignation_name
        doc.supervisor = supervisor
        
        item = doc.append("employees", {
            "employee": employee_name,
            "reason": reason,
            "employee_name": emp_data.get("employee_name"),
            "designation": emp_data.get("designation"),
            "project_allocation": emp_data.get("project")
        })

        doc.insert(ignore_permissions=True)
        
        if attachment:
            handle_attachment_internal(doc, item, attachment, "withdrawal_letter")

        doc.db_set("workflow_state", "Pending Supervisor")
        
        if supervisor:
            from frappe.desk.form.assign_to import add as add_assign
            try:
                add_assign({
                    "assign_to": [supervisor],
                    "doctype": doc.doctype,
                    "name": doc.name,
                    "description": "Review Resignation Withdrawal Request"
                })
            except: pass
            
        return {"status": "success", "message": "Withdrawal submitted", "name": doc.name}
    except Exception as e:
        frappe.log_error("Withdrawal Error", frappe.get_traceback())
        frappe.throw(str(e), frappe.ValidationError)

def handle_attachment_internal(doc, row, attachment_data, field_name):
    if isinstance(attachment_data, str):
        try: attachment_data = json.loads(attachment_data)
        except: return
            
    file_name = attachment_data.get('attachment_name')
    file_base64 = attachment_data.get('attachment')
    
    if file_name and file_base64:
        try:
            content = base64.b64decode(file_base64)
            saved_file = save_file(file_name, content, doc.doctype, doc.name, is_private=1, folder="Home/Attachments")
            frappe.db.set_value(row.doctype, row.name, field_name, saved_file.file_url)
        except: pass

@frappe.whitelist()
def get_supervisor_dropdown():
    return frappe.get_all("User", filters={"enabled": 1, "user_type": "System User"}, fields=["name", "full_name"])

@frappe.whitelist()
def get_my_active_resignation(employee_id=None, **kwargs):
    # With token auth, query params are NOT in form_dict — read from request.args directly
    input_id = (frappe.request.args.get('employee_id') if hasattr(frappe, 'request') else None) \
        or frappe.form_dict.get('employee_id') or employee_id
    employee_name = resolve_employee_name(input_id)
    if not employee_name: return None

    # States where the employee must take action — show these first
    EMPLOYEE_ACTION_STATES = [
        "Pending Relieving Date Correction",
        "Draft",
    ]

    seen = set()
    items = frappe.get_all("Employee Resignation Item",
        filters={"employee": employee_name, "parenttype": "Employee Resignation"},
        fields=["parent"], order_by="creation desc")

    all_records = []
    for item in items:
        if item.parent in seen:
            continue
        seen.add(item.parent)
        doc = frappe.get_doc("Employee Resignation", item.parent)
        # Skip terminal states
        if doc.workflow_state in ("Resigned", "Cancelled", "Resignation Withdrawn"):
            continue
        all_records.append({
            "name": doc.name,
            "workflow_state": doc.workflow_state,
            "resignation_initiation_date": doc.resignation_initiation_date,
            "relieving_date": doc.relieving_date,
            "creation": str(doc.creation)
        })

    if not all_records:
        return None

    # Prioritize records where employee needs to act
    for record in all_records:
        if record["workflow_state"] in EMPLOYEE_ACTION_STATES:
            return record

    # Fallback: most recent active record
    return all_records[0]


@frappe.whitelist()
def get_all_my_resignations(employee_id=None, **kwargs):
    # With token auth, query params are NOT in form_dict — read from request.args directly
    input_id = (frappe.request.args.get('employee_id') if hasattr(frappe, 'request') else None) \
        or frappe.form_dict.get('employee_id') or employee_id
    employee_name = resolve_employee_name(input_id)
    if not employee_name: return []

    items = frappe.get_all("Employee Resignation Item", 
        filters={"employee": employee_name, "parenttype": "Employee Resignation"},
        fields=["parent"], order_by="creation desc")
    
    results = []
    seen = set()
    for item in items:
        if item.parent in seen: continue
        doc = frappe.get_doc("Employee Resignation", item.parent)
        results.append({
            "name": doc.name,
            "workflow_state": doc.workflow_state,
            "resignation_initiation_date": doc.resignation_initiation_date,
            "relieving_date": doc.relieving_date,
            "creation": doc.creation
        })
        seen.add(item.parent)
    return results

@frappe.whitelist()
def get_employee_supervisor(employee_id=None, **kwargs):
    from one_fm.utils import get_approver
    # With token auth, query params are NOT in form_dict — read from request.args directly
    input_id = (frappe.request.args.get('employee_id') if hasattr(frappe, 'request') else None) \
        or frappe.form_dict.get('employee_id') or employee_id
    employee_name = resolve_employee_name(input_id)
    if not employee_name: return {}

    approver_name = get_approver(employee_name)
    if not approver_name: return {}
    
    supervisor = frappe.db.get_value("Employee", approver_name, ["user_id", "employee_name"], as_dict=True)
    if supervisor and supervisor.get("user_id"):
        return {"user_id": supervisor.get("user_id"), "full_name": supervisor.get("employee_name")}
    return {}

@frappe.whitelist()
def correct_resignation_date_app(
    employee_id=None,
    resignation_id=None,
    new_date=None,
    new_initiation_date=None,
    attachment=None,
    attachment_name=None,
    data=None,
    **kwargs
):
    """
    Handles the 'Pending Relieving Date Correction' action from the mobile app.
    Payload: employee_id, resignation_id, new_date (relieving), new_initiation_date, attachment (base64), attachment_name
    """
    try:
        # Token auth: read from raw body (POST) — same pattern as create_resignation
        if not resignation_id:
            payload = get_request_data(data, **kwargs)
            employee_id = employee_id or payload.get('employee_id')
            resignation_id = payload.get('resignation_id')
            new_date = new_date or payload.get('new_date')
            new_initiation_date = new_initiation_date or payload.get('new_initiation_date')
            attachment = attachment or payload.get('attachment')
            attachment_name = attachment_name or payload.get('attachment_name', 'resignation_letter.png')

        if not resignation_id:
            frappe.throw("resignation_id is required", frappe.ValidationError)
        if not new_date:
            frappe.throw("new_date (relieving date) is required", frappe.ValidationError)

        doc = frappe.get_doc("Employee Resignation", resignation_id)

        if doc.workflow_state != "Pending Relieving Date Correction":
            frappe.throw(
                f"Cannot correct date. Current state: {doc.workflow_state}",
                frappe.ValidationError
            )

        # Update dates
        doc.relieving_date = new_date
        if new_initiation_date:
            doc.resignation_initiation_date = new_initiation_date

        # Update dates in child table rows too
        for row in doc.employees:
            row.resignation_letter_date = new_date

        # Handle attachment if provided
        if attachment:
            att_name = attachment_name or "corrected_resignation_letter.png"
            handle_attachment_internal(doc, doc, {
                "attachment_name": att_name,
                "attachment": attachment
            }, "resignation_letter")

        # Save and advance workflow
        doc.save(ignore_permissions=True)
        doc.db_set("workflow_state", "Pending Supervisor")
        frappe.db.commit()

        return {
            "status": "success",
            "message": "Resignation date corrected and resubmitted to supervisor",
            "name": doc.name
        }

    except Exception as e:
        frappe.log_error("Correction Error", frappe.get_traceback())
        frappe.throw(str(e), frappe.ValidationError)
