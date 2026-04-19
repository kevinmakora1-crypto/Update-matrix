import frappe

def run():
	wf = frappe.get_doc("Workflow", "Employee Resignation")
	wf.set("states", [])
	wf.set("transitions", [])
	
	states_data = [
		{"state": "Draft", "doc_status": 0, "update_field": "status", "update_value": "Pending", "allow_edit": "Employee", "style": "Primary"},
		{"state": "Pending Supervisor", "doc_status": 0, "update_field": "status", "update_value": "Pending", "allow_edit": "Employee", "style": "Warning"},
		{"state": "Pending Relieving Date Correction", "doc_status": 0, "update_field": "status", "update_value": "Pending", "allow_edit": "Employee", "style": "Danger"},
		{"state": "Pending Operations Manager", "doc_status": 0, "update_field": "status", "update_value": "Pending", "allow_edit": "Operations Manager", "style": "Warning"},
		{"state": "Approved", "doc_status": 1, "update_field": "status", "update_value": "Approved", "allow_edit": "System Manager", "style": "Success"},
		{"state": "Withdrawn", "doc_status": 1, "update_field": "status", "update_value": "Withdrawn", "allow_edit": "System Manager", "style": "Inverse"}
	]
	for s in states_data:
		wf.append("states", s)
	
	transitions_data = [
		{"state": "Draft", "action": "Submit to Supervisor", "next_state": "Pending Supervisor", "allowed": "Employee"},
		{"state": "Pending Supervisor", "action": "Request Relieving Date Change", "next_state": "Pending Relieving Date Correction", "allowed": "Employee", "allowed_user_field": "supervisor"},
		{"state": "Pending Relieving Date Correction", "action": "Resubmit Date", "next_state": "Pending Supervisor", "allowed": "Employee"},
		{"state": "Pending Supervisor", "action": "Accept & Forward to OM", "next_state": "Pending Operations Manager", "allowed": "Employee", "allowed_user_field": "supervisor"},
		{"state": "Pending Operations Manager", "action": "Approve", "next_state": "Approved", "allowed": "Operations Manager"}
	]
	for t in transitions_data:
		wf.append("transitions", t)
		
	if not frappe.db.exists("Workflow Action Master", "Accept & Forward to OM"):
		frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": "Accept & Forward to OM"}).insert(ignore_permissions=True)
		
	wf.save(ignore_permissions=True)

	# Build Notification 1: First Submission / Resubmission
	if not frappe.db.exists("Notification", "Resignation - Offboarding Awareness"):
		notif = frappe.new_doc("Notification")
		notif.name = "Resignation - Offboarding Awareness"
		notif.document_type = "Employee Resignation"
		notif.subject = "Awareness: Resignation ({{ doc.name }}) is Pending Supervisor"
		notif.event = "Value Change"
		notif.value_changed = "workflow_state"
		notif.condition = "doc.workflow_state == 'Pending Supervisor'"
		notif.send_to_all_assignees = 0
		notif.channel = "Email"
		notif.message = """<p>A resignation has been submitted securely to the Supervisor: <b>{{ doc.name }}</b></p>
<p>Employee: {{ doc.full_name_in_english }}</p>
<p>Resignation Date: {{ doc.resignation_initiation_date }}</p>
<p>Relieving Date: {{ doc.relieving_date }}</p>
<br>
<p>This is a courtesy synchronization purely for Offboarding/Residency awareness.</p>"""
		notif.append("recipients", {"condition": "", "receiver_by_role": "Offboarding Officer"})
		notif.insert(ignore_permissions=True)
	else:
		notif = frappe.get_doc("Notification", "Resignation - Offboarding Awareness")
		notif.message = """<p>A resignation has been submitted securely to the Supervisor: <b>{{ doc.name }}</b></p>
<p>Employee: {{ doc.full_name_in_english }}</p>
<p>Resignation Date: {{ doc.resignation_initiation_date }}</p>
<p>Relieving Date: {{ doc.relieving_date }}</p>
<br>
<p>This is a courtesy synchronization purely for Offboarding/Residency awareness.</p>"""
		notif.condition = "doc.workflow_state == 'Pending Supervisor'"
		notif.save(ignore_permissions=True)
		
	# Clean up any generic "Pending Offboarding Officer" assignment rules if they exist
	if frappe.db.exists("Assignment Rule", "Resignation - Pending Offboarding Officer"):
		frappe.delete_doc("Assignment Rule", "Resignation - Pending Offboarding Officer", ignore_permissions=True)
	
	frappe.db.commit()

run()
