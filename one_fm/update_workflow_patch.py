import frappe

def run():
	wf = frappe.get_doc("Workflow", "Employee Resignation")
	wf.set("transitions", [])
	
	transitions_data = [
		{"state": "Draft", "action": "Submit to Supervisor", "next_state": "Pending Supervisor", "allowed": "Employee"},
		{"state": "Pending Supervisor", "action": "Request Relieving Date Change", "next_state": "Pending Relieving Date Correction", "allowed": "Employee", "allowed_user_field": "supervisor"},
		{"state": "Pending Relieving Date Correction", "action": "Resubmit Date", "next_state": "Pending Supervisor", "allowed": "Employee"},
		{"state": "Pending Supervisor", "action": "Submit to Offboarding", "next_state": "Pending Offboarding Officer", "allowed": "Employee", "allowed_user_field": "supervisor"},
		{"state": "Pending Offboarding Officer", "action": "Review Completed", "next_state": "Pending Operations Manager", "allowed": "Offboarding Officer"},
		{"state": "Pending Operations Manager", "action": "Approve", "next_state": "Approved", "allowed": "Operations Manager"}
	]
	for t in transitions_data:
		wf.append("transitions", t)
		
	if not frappe.db.exists("Workflow Action Master", "Submit to Supervisor"):
		frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": "Submit to Supervisor"}).insert(ignore_permissions=True)
	if not frappe.db.exists("Workflow Action Master", "Submit to Offboarding"):
		frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": "Submit to Offboarding"}).insert(ignore_permissions=True)
		
	wf.save(ignore_permissions=True)

	if not frappe.db.exists("Notification", "Resignation Initiated - Offboarding Awareness"):
		notif = frappe.new_doc("Notification")
		notif.name = "Resignation Initiated - Offboarding Awareness"
		notif.document_type = "Employee Resignation"
		notif.subject = "Awareness: Resignation Initiated - {{ doc.name }}"
		notif.event = "Value Change"
		notif.value_changed = "workflow_state"
		notif.condition = "doc.workflow_state == 'Pending Supervisor'"
		notif.send_to_all_assignees = 0
		notif.channel = "Email"
		notif.message = "<p>A resignation has been submitted to the Supervisor. This is a courtesy notification.</p>"
		notif.append("recipients", {"condition": "", "receiver_by_role": "Offboarding Officer"})
		notif.insert(ignore_permissions=True)
	
	frappe.db.commit()

run()
