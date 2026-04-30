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
    
    doc.relieving_date = frappe.db.get_value("Employee Resignation", employee_resignation, "relieving_date") or frappe.utils.today()
    doc.workflow_state = "Pending Supervisor"
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

@frappe.whitelist(allow_guest=False)
def get_my_active_resignation(employee_id=None):
    if not employee_id:
        return None
    docs = frappe.get_all("Employee Resignation Item", filters={"employee": employee_id, "parenttype": "Employee Resignation", "docstatus": ["!=", 2]}, fields=["parent"])
    if docs:
        doc = frappe.get_doc("Employee Resignation", docs[0].parent)
        if doc.workflow_state not in ["Rejected", "Withdrawn"]:
            return doc.as_dict()
    return None

@frappe.whitelist(allow_guest=False)
def get_all_my_resignations(employee_id=None):
    if not employee_id:
        return []
    docs = frappe.get_all("Employee Resignation Item", filters={"employee": employee_id, "parenttype": "Employee Resignation", "docstatus": ["!=", 2]}, fields=["parent"])
    res = []
    for d in docs:
        res.append(frappe.get_doc("Employee Resignation", d.parent).as_dict())
    return res

@frappe.whitelist(allow_guest=False)
def get_employee_supervisor(employee_id=None):
    if not employee_id:
        return None
    reports_to = frappe.db.get_value("Employee", {"employee": employee_id}, "reports_to")
    if reports_to:
        return reports_to
    # fallback to name if employee_id is actually the name
    return frappe.db.get_value("Employee", employee_id, "reports_to")


@frappe.whitelist(allow_guest=True)
def extend_resignation(data=None, employee_id=None, supervisor=None, attachment=None, extended_date=None, resignation_id=None):
	try:
		if data:
			import json
			parsed = json.loads(data)
			employee_id = parsed.get("employee_id")
			supervisor = parsed.get("supervisor")
			attachment = parsed.get("attachment")
			extended_date = parsed.get("extended_date")
			resignation_id = parsed.get("resignation_id")

		if not employee_id or not resignation_id or not extended_date:
			return {"message": "Missing mandatory fields", "code": 400}

		# Fetch Employee
		emp = frappe.db.get_value("Employee", {"name": employee_id}, ["name", "employee_name", "designation", "employment_type", "project", "relieving_date"], as_dict=True)
		if not emp:
			return {"message": "Employee not found", "code": 404}

		doc = frappe.new_doc("Employee Resignation Extension")
		doc.supervisor = supervisor
		doc.employee_resignation = resignation_id
		doc.current_relieving_date = emp.relieving_date
		doc.extended_relieving_date = extended_date

		doc.append("employees", {
			"employee": emp.name,
			"employee_id": employee_id,
			"employee_name": emp.employee_name,
			"designation": emp.designation,
			"employment_type": emp.employment_type,
			"project_allocation": emp.project,
			"reason": "Extended via Mobile App",
			"extension_status": "Pending"
		})

		doc.insert(ignore_permissions=True)
		doc.db_set("workflow_state", "Pending Supervisor")

		if supervisor:
			from frappe.desk.form.assign_to import add as add_assign
			try:
				add_assign({
					"assign_to": [supervisor],
					"doctype": doc.doctype,
					"name": doc.name,
					"description": "Review Employee Resignation Extension"
				})
			except Exception:
				pass

		if attachment:
			handle_attachment(doc, attachment)
			
			# Attach to employee profile
			employee_doc = frappe.get_doc("Employee", emp.name)
			try:
				from frappe.utils.file_manager import save_file
				import base64
				format, imgstr = attachment.split(";base64,")
				ext = format.split("/")[-1]
				save_file(f"Extension-{employee_id}.{ext}", base64.b64decode(imgstr), "Employee", emp.name, is_private=1)
			except Exception as e:
				pass

		return {"message": "Resignation Extension Submitted successfully", "code": 200}
	except Exception as e:
		frappe.log_error(title="Extend Resignation API Error", message=frappe.get_traceback())
		return {"message": str(e), "code": 500}


@frappe.whitelist(allow_guest=True)
def correct_resignation_date_app(data=None, employee_id=None, new_date=None, attachment=None, resignation_id=None):
	try:
		if data:
			import json
			parsed = json.loads(data)
			employee_id = parsed.get("employee_id")
			new_date = parsed.get("new_date")
			attachment = parsed.get("attachment")
			resignation_id = parsed.get("resignation_id")

		if not employee_id or not resignation_id or not new_date:
			return {"message": "Missing mandatory fields", "code": 400}

		# Fetch exact Parent
		if not frappe.db.exists("Employee Resignation", resignation_id):
			return {"message": "Resignation Not Found", "code": 404}
			
		doc = frappe.get_doc("Employee Resignation", resignation_id)
		if doc.workflow_state != "Pending Relieving Date Correction":
			return {"message": "Resignation is not strictly pending date correction", "code": 400}

		# Set structural date property explicitly
		doc.relieving_date = new_date

		# Manage Base64 Filesystem attachment completely independently but securely link
		if attachment:
			# File handling
			try:
				from frappe.utils.file_manager import save_file
				import base64
				format, imgstr = attachment.split(";base64,")
				ext = format.split("/")[-1]
				save_file(f"Resignation-Date-Corrected-{employee_id}.{ext}", base64.b64decode(imgstr), "Employee Resignation", doc.name, is_private=1)
			except Exception as e:
				pass

		# Resubmit completely structurally via Workflow framework
		# Action string relies entirely upon exact schema matrix
		from frappe.model.workflow import apply_workflow
		apply_workflow(doc, "Resubmit Date")
		doc.save(ignore_permissions=True)

		return {"message": "Correction Submited Successfully", "code": 200}
	except Exception as e:
		frappe.log_error(title="Resignation Correction API Error", message=frappe.get_traceback())
		return {"message": str(e), "code": 500}
