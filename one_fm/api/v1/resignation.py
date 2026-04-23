import frappe
from frappe import _
import json

@frappe.whitelist(allow_guest=False)
def create_resignation(data=None, employee_id=None, supervisor=None, attachment=None):
    # CapacitorHttp sends flat form params; also support JSON-encoded 'data' string
    resignation_initiation_date = None
    relieving_date = None
    
    if data:
        if isinstance(data, str):
            data = json.loads(data)
        employee_id = data.get('employee_id') or employee_id
        supervisor = data.get('supervisor') or supervisor
        attachment = data.get('attachment') or attachment
        resignation_initiation_date = data.get('resignation_initiation_date')
        relieving_date = data.get('relieving_date')
    
    # Unconditionally resolve human-readable employee_id to the primary key name
    if employee_id:
        actual_employee_name = frappe.db.get_value("Employee", {"employee_id": employee_id}, "name")
        if actual_employee_name:
            employee_id = actual_employee_name
            
    if isinstance(attachment, str):
        try:
            attachment = json.loads(attachment)
        except Exception:
            pass
    
    doc = frappe.new_doc("Employee Resignation")
    
    if resignation_initiation_date:
        doc.resignation_initiation_date = resignation_initiation_date
    if relieving_date:
        doc.relieving_date = relieving_date
        
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
        doc.reload() # Sync the in-memory object with the db_set from handle_attachment
        
    from frappe.model.workflow import apply_workflow
    apply_workflow(doc, "Submit to Supervisor")
    
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

    if employee_id:
        actual_employee_name = frappe.db.get_value("Employee", {"employee_id": employee_id}, "name")
        if actual_employee_name:
            employee_id = actual_employee_name

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
        
    doc.relieving_date = frappe.db.get_value("Employee Resignation", employee_resignation, "relieving_date")
        
    emp_data = frappe.db.get_value("Employee", employee_id, ["employee_name", "first_name", "designation", "project"], as_dict=True) or {}
    
    doc.append("employees", {
        "employee": employee_id,
        "reason": reason,
        "employee_name": emp_data.get("employee_name") or emp_data.get("first_name"),
        "designation": emp_data.get("designation"),
        "project_allocation": emp_data.get("project")
    })
    
    doc.insert(ignore_permissions=True)
    
    if attachment:
        handle_attachment(doc, attachment)
        doc.reload() # Sync the in-memory object with the db_set from handle_attachment
    
    return doc.name

def handle_attachment(doc, attachment_data):
    import base64
    from frappe.utils.file_manager import save_file
    
    file_name = None
    file_base64 = None
    
    if isinstance(attachment_data, str):
        if attachment_data.startswith("data:"):
            # It's a raw base64 data string!
            file_base64 = attachment_data
            
            # Guess extension from MIME type
            ext = "pdf"
            try:
                ext = attachment_data.split(";")[0].split("/")[1]
            except Exception:
                pass
            file_name = f"Attachment-{doc.name}.{ext}"
        else:
            # It might be a JSON string, or it might just be pure base64 without data prefix!
            try:
                parsed = json.loads(attachment_data)
                if isinstance(parsed, dict):
                    file_name = parsed.get('attachment_name')
                    file_base64 = parsed.get('attachment')
            except Exception:
                # If json.loads fails, it's just pure base64 string without data prefix!
                file_base64 = attachment_data
                ext = "pdf"
                if file_base64.startswith("/9j/"):
                    ext = "jpg"
                elif file_base64.startswith("iVBORw0K"):
                    ext = "png"
                elif file_base64.startswith("JVBER"):
                    ext = "pdf"
                else:
                    ext = "jpg" # Fallback to jpg for mobile uploads
                file_name = f"Attachment-{doc.name}.{ext}" 
    elif isinstance(attachment_data, dict):
        file_name = attachment_data.get('attachment_name')
        file_base64 = attachment_data.get('attachment')
        
    if file_name and file_base64:
        # Strip data URL prefix if present
        if "," in file_base64 and file_base64.startswith("data:"):
            file_base64 = file_base64.split(",")[1]
        
        # Add padding if missing
        missing_padding = len(file_base64) % 4
        if missing_padding:
            file_base64 += '=' * (4 - missing_padding)
            
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
            elif doc.doctype == "Employee Resignation Extension":
                frappe.db.set_value(row.doctype, row.name, "extension_letter", saved_file.file_url)
            else:
                frappe.db.set_value(row.doctype, row.name, "resignation_letter", saved_file.file_url)

@frappe.whitelist(allow_guest=False)
def get_supervisor_dropdown():
    # Return available users to act as supervisor
    return frappe.get_all("User", filters={"enabled": 1, "user_type": "System User"}, fields=["name", "full_name"])

@frappe.whitelist(allow_guest=False)
def get_my_active_resignation(employee_id=None):
    if not employee_id:
        employee_id = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        
    emp_name = frappe.db.get_value("Employee", {"employee_id": employee_id}, "name", cache=True) or employee_id

    # Fetch the parent Employee Resignation directly from the child component matrix
    active_items = frappe.get_all("Employee Resignation Item", 
        filters={"employee": emp_name, "parenttype": "Employee Resignation"},
        fields=["parent"],
        order_by="creation desc",
        limit=1
    )
    
    if not active_items:
        return {}
        
    parent_id = active_items[0].parent
    
    doc = frappe.get_doc("Employee Resignation", parent_id)
    
    # Organically skip cancelled or entirely withdrawn/completed documents
    if doc.docstatus == 2 or doc.workflow_state in ["Resignation Withdrawn", "Cancelled"]:
        return {}
        
    return {
        "name": doc.name,
        "workflow_state": doc.workflow_state,
        "resignation_initiation_date": doc.resignation_initiation_date,
        "relieving_date": doc.relieving_date,
        "creation": doc.creation
    }


@frappe.whitelist(allow_guest=True)
def extend_resignation(data=None, employee_id=None, supervisor=None, attachment=None, extended_date=None, resignation_id=None, reason=None):
	try:
		if data:
			import json
			parsed = json.loads(data)
			employee_id = parsed.get("employee_id")
			supervisor = parsed.get("supervisor")
			attachment = parsed.get("attachment")
			extended_date = parsed.get("extended_date")
			reason = parsed.get("reason")
			resignation_id = parsed.get("resignation_id")

		if employee_id:
			actual_employee_name = frappe.db.get_value("Employee", {"employee_id": employee_id}, "name")
			if actual_employee_name:
				employee_id = actual_employee_name

		if not employee_id or not resignation_id or not extended_date:
			frappe.throw("Missing mandatory fields")

		emp = frappe.db.get_value("Employee", {"name": employee_id}, ["name", "employee_name", "relieving_date"], as_dict=True)
		if not emp:
			frappe.throw("Employee not found")

		doc = frappe.new_doc("Employee Resignation Extension")
		doc.supervisor = supervisor
		doc.employee_resignation = resignation_id
		doc.current_relieving_date = emp.relieving_date
		doc.extended_relieving_date = extended_date

		doc.append("employees", {
			"employee": emp.name,
			"employee_name": emp.employee_name,
			"reason": reason
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

		return {"message": "Resignation Extension Submitted successfully"}
	except Exception as e:
		frappe.log_error(title="Extend Resignation API Error", message=frappe.get_traceback())
		frappe.throw(str(e))


@frappe.whitelist(allow_guest=True)
def correct_resignation_date_app(data=None, employee_id=None, new_date=None, attachment=None, resignation_id=None):
	try:
		if data:
			import json
			parsed = json.loads(data)
			employee_id = parsed.get("employee_id")
			new_date = parsed.get("new_date")
			new_initiation_date = parsed.get("new_initiation_date")
			attachment = parsed.get("attachment")
			resignation_id = parsed.get("resignation_id")

		if employee_id:
			actual_employee_name = frappe.db.get_value("Employee", {"employee_id": employee_id}, "name")
			if actual_employee_name:
				employee_id = actual_employee_name

		if not employee_id or not resignation_id or not new_date:
			frappe.throw("Missing mandatory fields")

		# Fetch exact Parent
		if not frappe.db.exists("Employee Resignation", resignation_id):
			frappe.throw("Resignation Not Found")
			
		doc = frappe.get_doc("Employee Resignation", resignation_id)
		if doc.workflow_state != "Pending Relieving Date Correction":
			frappe.throw("Resignation is not strictly pending date correction")

		# Set structural date property explicitly
		doc.relieving_date = new_date
		if new_initiation_date:
			doc.resignation_initiation_date = new_initiation_date

		# Must save BEFORE apply_workflow, because apply_workflow calls doc.load_from_db() and wipes unsaved properties!
		doc.save(ignore_permissions=True)
		frappe.db.commit()

		if attachment:
			# Use the robust global handler which automatically links the file to the row's resignation_letter field
			try:
				handle_attachment(doc, attachment)
				doc.reload() # Sync the in-memory object with the db_set from handle_attachment
			except Exception as e:
				frappe.log_error(title="Date Change Attachment Error", message=frappe.get_traceback())
				pass

		# Resubmit completely structurally via Workflow framework
		from frappe.model.workflow import apply_workflow
		apply_workflow(doc, "Resubmit Date")
		doc.save(ignore_permissions=True)

		return {"status": "success", "message": "Correction Submitted Successfully"}
	except Exception as e:
		frappe.log_error(title="Resignation Correction API Error", message=frappe.get_traceback())
		frappe.throw(str(e))

@frappe.whitelist(allow_guest=False)
def get_all_my_resignations(employee_id=None):
    if not employee_id:
        employee_id = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        
    emp_name = frappe.db.get_value("Employee", {"employee_id": employee_id}, "name", cache=True) or employee_id

    # Fetch the parent Employee Resignation directly from the child component matrix
    items = frappe.get_all("Employee Resignation Item", 
        filters={"employee": emp_name, "parenttype": "Employee Resignation"},
        fields=["parent"],
        order_by="creation desc"
    )
    
    if not items:
        return []
        
    results = []
    for item in items:
        try:
            doc = frappe.get_doc("Employee Resignation", item.parent)
            results.append({
                "name": doc.name,
                "workflow_state": doc.workflow_state,
                "resignation_initiation_date": doc.resignation_initiation_date,
                "relieving_date": doc.relieving_date,
                "creation": doc.creation
            })
        except Exception:
            pass
            
    return results


@frappe.whitelist()
def get_employee_supervisor(employee_id):
	from one_fm.utils import get_approver
	
	if not employee_id:
		return {}
	
	employee_name = frappe.db.get_value("Employee", {"employee_id": employee_id}, "name")
	if not employee_name:
		return {}

	approver_employee = get_approver(employee_name)
	if not approver_employee:
		return {}
	
	supervisor = frappe.db.get_value("Employee", approver_employee, ["user_id", "employee_name"], as_dict=True)
	if supervisor and supervisor.get("user_id"):
		return {
			"user_id": supervisor.get("user_id"),
			"full_name": supervisor.get("employee_name")
		}
	return {}
