import frappe
import json
import base64
from frappe import _
from frappe.utils.file_manager import save_file
from one_fm.api.mobile_utils import get_param, get_all_params


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def resolve_employee_name(employee_id):
    """Resolves a custom employee_id (e.g. '2202025NP191') to the Frappe PK
    (e.g. 'HR-EMP-01873').  Also accepts the PK directly as a fallback."""
    if not employee_id:
        return None
    name = frappe.db.get_value("Employee", {"employee_id": employee_id}, "name")
    if name:
        return name
    if frappe.db.exists("Employee", employee_id):
        return employee_id
    return None


def handle_attachment_internal(doc, row, attachment_data, field_name):
    """Saves a base64 attachment and links it to field_name on row."""
    if isinstance(attachment_data, str):
        try:
            attachment_data = json.loads(attachment_data)
        except Exception:
            return

    file_name = attachment_data.get("attachment_name")
    file_base64 = attachment_data.get("attachment")

    if file_name and file_base64:
        try:
            content = base64.b64decode(file_base64)
            saved_file = save_file(
                file_name, content, doc.doctype, doc.name,
                is_private=1, folder="Home/Attachments"
            )
            frappe.db.set_value(row.doctype, row.name, field_name, saved_file.file_url)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Public API endpoints
# ---------------------------------------------------------------------------

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
        p = get_all_params(
            "resignation_initiation_date", "relieving_date", "attachment",
            employee_id=employee_id,
            supervisor=supervisor,
        )
        input_id   = p["employee_id"]
        supervisor = p["supervisor"]
        init_date  = p["resignation_initiation_date"]
        rel_date   = p["relieving_date"] or get_param("resignation_date")
        attachment = p["attachment"]

        employee_name = resolve_employee_name(input_id)
        if not employee_name:
            frappe.throw(f"Employee '{input_id}' not found", frappe.ValidationError)

        emp = frappe.db.get_value(
            "Employee", employee_name,
            ["employee_name", "designation", "project", "department",
             "employment_type", "reports_to"],
            as_dict=True
        )

        # Fetch the employee's linked user_id so the record is owned by them on the desk
        employee_user = frappe.db.get_value("Employee", employee_name, "user_id")

        doc = frappe.new_doc("Employee Resignation")
        doc.owner = employee_user or frappe.session.user
        doc.resignation_initiation_date = init_date
        doc.relieving_date = rel_date
        doc.supervisor = supervisor
        doc.department = emp.get("department")
        doc.employment_type = emp.get("employment_type")
        doc.project_allocation = emp.get("project")
        doc.designation = emp.get("designation")
        # Insert as Draft first so validate() doesn't block on missing letter
        doc.workflow_state = "Draft"

        doc.append("employees", {
            "employee": employee_name,
            "employee_name": emp.get("employee_name"),
            "designation": emp.get("designation"),
            "project_allocation": emp.get("project"),
            "employment_type": emp.get("employment_type"),
            "resignation_letter_date": rel_date,
        })

        doc.insert(ignore_permissions=True)

        # Step 2: Attach the letter (must happen after insert so the row has a name)
        if attachment:
            att_str = attachment if isinstance(attachment, str) else json.dumps(attachment)
            try:
                att_data = json.loads(att_str) if isinstance(att_str, str) else att_str
            except Exception:
                att_data = {"attachment_name": "resignation_letter.png", "attachment": att_str}
            
            # The row we appended earlier
            row = doc.employees[0]
            handle_attachment_internal(doc, row, att_data, "resignation_letter")

        # Step 3: Advance to Pending Supervisor now that the letter is saved
        doc.db_set("workflow_state", "Pending Supervisor")
        frappe.db.commit()
        return {"status": "success", "message": "Resignation submitted successfully", "name": doc.name}

    except Exception as e:
        frappe.log_error("Create Resignation Error", frappe.get_traceback())
        frappe.throw(str(e), frappe.ValidationError)


@frappe.whitelist()
def extend_resignation(
    employee_id=None,
    supervisor=None,
    reason=None,
    extended_date=None,
    resignation_id=None,
    attachment=None,
    data=None,
    **kwargs
):
    """Create an Employee Resignation Extension for the employee's active resignation."""
    try:
        p = get_all_params(
            "reason", "extended_date", "attachment",
            employee_id=employee_id,
            supervisor=supervisor,
            resignation_id=resignation_id,
        )
        input_id       = p["employee_id"]
        supervisor     = p["supervisor"]
        reason         = p["reason"]
        extended_date  = p["extended_date"]
        resignation_id = p["resignation_id"]
        attachment     = p["attachment"]

        employee_name = resolve_employee_name(input_id)
        if not employee_name:
            frappe.throw(f"Employee '{input_id}' not found", frappe.ValidationError)
        if not extended_date:
            frappe.throw("extended_date is required", frappe.ValidationError)

        # Find active resignation if not supplied
        if not resignation_id:
            items = frappe.get_all(
                "Employee Resignation Item",
                filters={"employee": employee_name, "parenttype": "Employee Resignation"},
                fields=["parent"], order_by="creation desc"
            )
            TERMINAL = {"Resigned", "Cancelled", "Resignation Withdrawn"}
            for item in items:
                d = frappe.get_doc("Employee Resignation", item.parent)
                if d.workflow_state not in TERMINAL:
                    resignation_id = item.parent
                    break

        if not resignation_id:
            frappe.throw("No active resignation found to extend", frappe.ValidationError)

        active_doc = frappe.get_doc("Employee Resignation", resignation_id)
        employee_user = frappe.db.get_value("Employee", employee_name, "user_id")

        ext = frappe.new_doc("Employee Resignation Extension")
        ext.owner = employee_user or frappe.session.user
        ext.employee_resignation = resignation_id
        ext.supervisor = supervisor or active_doc.supervisor
        ext.reason = reason or "Extension requested by employee"
        # Ensure we only extract the date part (YYYY-MM-DD) if it's an ISO timestamp
        frappe.log_error("Extension Received Date", str(extended_date))
        parsed_date = extended_date.split('T')[0] if isinstance(extended_date, str) else extended_date
        ext.extended_relieving_date = parsed_date
        # Do NOT set workflow_state before insert — Frappe sets it to the
        # workflow's initial state ('Pending Supervisor') automatically

        for row in active_doc.employees:
            ext.append("employees", {
                "employee": row.employee,
                "employee_name": row.employee_name,
                "reason": reason or "Extension requested by employee",
            })

        ext.insert(ignore_permissions=True)

        # Attach letter after insert so the row has a name
        if attachment:
            att_str = attachment if isinstance(attachment, str) else json.dumps(attachment)
            try:
                att_data = json.loads(att_str) if isinstance(att_str, str) else att_str
            except Exception:
                att_data = {"attachment_name": "extension_letter.png", "attachment": att_str}
            
            # Attach to the child row (Employee Resignation Extension Item)
            if ext.employees:
                handle_attachment_internal(ext, ext.employees[0], att_data, "extension_letter")
            frappe.db.commit()

        return {
            "status": "success",
            "message": "Resignation extension submitted successfully",
            "name": ext.name
        }

    except Exception as e:
        frappe.log_error("Extension Error", frappe.get_traceback())
        frappe.throw(str(e), frappe.ValidationError)


@frappe.whitelist()
def withdraw_resignation(
    employee_id=None,
    reason=None,
    attachment=None,
    data=None,
    **kwargs
):
    try:
        p = get_all_params(
            "reason", "attachment",
            employee_id=employee_id,
        )
        input_id   = p["employee_id"]
        reason     = p["reason"]
        attachment = p["attachment"]

        employee_name = resolve_employee_name(input_id)
        if not employee_name:
            frappe.throw(f"Employee '{input_id}' not found", frappe.ValidationError)

        # Find the most recent active resignation
        items = frappe.get_all(
            "Employee Resignation Item",
            filters={"employee": employee_name, "parenttype": "Employee Resignation"},
            fields=["parent"],
            order_by="creation desc"
        )

        active_doc = None
        for item in items:
            d = frappe.get_doc("Employee Resignation", item.parent)
            if d.workflow_state not in ("Resigned", "Cancelled", "Resignation Withdrawn"):
                active_doc = d
                break

        if not active_doc:
            frappe.throw("No active resignation found to withdraw", frappe.ValidationError)

        employee_user = frappe.db.get_value("Employee", employee_name, "user_id")
        withdrawal = frappe.new_doc("Employee Resignation Withdrawal")
        withdrawal.owner = employee_user or frappe.session.user
        withdrawal.employee_resignation = active_doc.name
        withdrawal.reason = reason or "Employee-initiated withdrawal"
        # Do NOT set workflow_state before insert — Frappe sets it to the
        # workflow's initial state ('Pending Supervisor') automatically

        for row in active_doc.employees:
            withdrawal.append("employees", {
                "employee": row.employee,
                "employee_name": row.employee_name,
                "reason": reason or "Employee-initiated withdrawal",
            })

        withdrawal.insert(ignore_permissions=True)

        if attachment:
            att_str = attachment if isinstance(attachment, str) else json.dumps(attachment)
            try:
                att_data = json.loads(att_str) if isinstance(att_str, str) else att_str
            except Exception:
                att_data = {"attachment_name": "withdrawal_letter.png", "attachment": att_str}
                
            if withdrawal.employees:
                handle_attachment_internal(withdrawal, withdrawal.employees[0], att_data, "attachment")
            frappe.db.commit()

        # Notify offboarding officer
        try:
            offboarding_officer = frappe.db.get_single_value(
                "HR Settings", "offboarding_officer"
            ) if frappe.db.exists("DocType", "HR Settings") else None
            if offboarding_officer:
                frappe.share.add(
                    "Employee Resignation Withdrawal", withdrawal.name,
                    user=offboarding_officer, read=1, notify=1,
                    flags={"ignore_share_permission": True}
                )
        except Exception:
            pass

        return {"status": "success", "message": "Withdrawal submitted", "name": withdrawal.name}

    except Exception as e:
        frappe.log_error("Withdrawal Error", frappe.get_traceback())
        frappe.throw(str(e), frappe.ValidationError)


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
    try:
        p = get_all_params(
            "new_date", "new_initiation_date", "attachment", "attachment_name",
            employee_id=employee_id,
            resignation_id=resignation_id,
        )
        input_id         = p["employee_id"]
        resignation_id   = p["resignation_id"]
        new_date         = p["new_date"]
        new_initiation   = p["new_initiation_date"]
        attachment       = p["attachment"]
        att_name         = p["attachment_name"] or "corrected_resignation_letter.png"

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

        doc.relieving_date = new_date
        if new_initiation:
            doc.resignation_initiation_date = new_initiation

        for row in doc.employees:
            row.resignation_letter_date = new_date

        if attachment:
            att_str = attachment if isinstance(attachment, str) else json.dumps(attachment)
            try:
                att_data = json.loads(att_str) if isinstance(att_str, str) else att_str
            except Exception:
                att_data = {"attachment_name": att_name, "attachment": att_str}
            if doc.employees:
                handle_attachment_internal(doc, doc.employees[0], att_data, "resignation_letter")

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


@frappe.whitelist()
def get_supervisor_dropdown():
    return frappe.get_all(
        "User",
        filters={"enabled": 1, "user_type": "System User"},
        fields=["name", "full_name"]
    )


@frappe.whitelist()
def get_my_active_resignation(employee_id=None, **kwargs):
    """Returns a single resignation record the employee should act on next,
    prioritising states that require employee action over waiting states."""
    input_id = get_param("employee_id", employee_id)
    employee_name = resolve_employee_name(input_id)
    if not employee_name:
        return None

    EMPLOYEE_ACTION_STATES = ["Pending Relieving Date Correction", "Draft"]
    TERMINAL_STATES = {"Resigned", "Cancelled", "Withdrawn"}

    seen = set()
    items = frappe.get_all(
        "Employee Resignation Item",
        filters={"employee": employee_name, "parenttype": "Employee Resignation"},
        fields=["parent"],
        order_by="creation desc"
    )

    all_records = []
    for item in items:
        if item.parent in seen:
            continue
        seen.add(item.parent)
        doc = frappe.get_doc("Employee Resignation", item.parent)
        if doc.workflow_state in TERMINAL_STATES:
            continue
        all_records.append({
            "name": doc.name,
            "workflow_state": doc.workflow_state,
            "resignation_initiation_date": doc.resignation_initiation_date,
            "relieving_date": doc.relieving_date,
            "creation": str(doc.creation),
            "supervisor": doc.supervisor,
            "supervisor_name": frappe.db.get_value("User", doc.supervisor, "full_name") if doc.supervisor else None
        })

    if not all_records:
        return None

    for record in all_records:
        if record["workflow_state"] in EMPLOYEE_ACTION_STATES:
            return record

    return all_records[0]


@frappe.whitelist()
def get_all_my_resignations(employee_id=None, **kwargs):
    """Returns all resignation records for the employee (history list)."""
    input_id = get_param("employee_id", employee_id)
    employee_name = resolve_employee_name(input_id)
    if not employee_name:
        return []

    seen = set()
    items = frappe.get_all(
        "Employee Resignation Item",
        filters={"employee": employee_name, "parenttype": "Employee Resignation"},
        fields=["parent"],
        order_by="creation desc"
    )

    results = []
    for item in items:
        if item.parent in seen:
            continue
        seen.add(item.parent)
        doc = frappe.get_doc("Employee Resignation", item.parent)
        
        results.append({
            "name": doc.name,
            "workflow_state": doc.workflow_state,
            "resignation_initiation_date": doc.resignation_initiation_date,
            "relieving_date": doc.relieving_date,
            "creation": str(doc.creation),
        })

    return results


@frappe.whitelist()
def get_employee_supervisor(employee_id=None, **kwargs):
    from one_fm.utils import get_approver
    input_id = get_param("employee_id", employee_id)
    employee_name = resolve_employee_name(input_id)
    if not employee_name:
        return {}

    approver_name = get_approver(employee_name)
    if not approver_name:
        return {}

    supervisor = frappe.db.get_value(
        "Employee", approver_name,
        ["user_id", "employee_name"], as_dict=True
    )
    if supervisor and supervisor.get("user_id"):
        return {"user_id": supervisor.get("user_id"), "full_name": supervisor.get("employee_name")}
    return {}
