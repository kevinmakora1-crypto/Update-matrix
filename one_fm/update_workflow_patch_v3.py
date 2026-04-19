import frappe

def run():
	wf = frappe.get_doc("Workflow", "Employee Resignation")
	wf.set("states", [])
	wf.set("transitions", [])
	
	states_data = [
		{"state": "Draft", "doc_status": 0, "update_field": "status", "update_value": "Pending", "allow_edit": "Employee", "style": "Primary"},
		{"state": "Pending Supervisor", "doc_status": 0, "update_field": "status", "update_value": "Pending", "allow_edit": "All", "style": "Warning"},
		{"state": "Pending Relieving Date Correction", "doc_status": 0, "update_field": "status", "update_value": "Pending", "allow_edit": "Employee", "style": "Danger"},
		{"state": "Pending Operations Manager", "doc_status": 0, "update_field": "status", "update_value": "Pending", "allow_edit": "Operations Manager", "style": "Warning"},
		{"state": "Approved", "doc_status": 1, "update_field": "status", "update_value": "Approved", "allow_edit": "System Manager", "style": "Success"},
		{"state": "Withdrawn", "doc_status": 1, "update_field": "status", "update_value": "Withdrawn", "allow_edit": "System Manager", "style": "Inverse"}
	]
	for s in states_data:
		wf.append("states", s)
	
	transitions_data = [
		{"state": "Draft", "action": "Submit to Supervisor", "next_state": "Pending Supervisor", "allowed": "Employee"},
		{"state": "Pending Supervisor", "action": "Request Relieving Date Change", "next_state": "Pending Relieving Date Correction", "allowed": "All"},
		{"state": "Pending Relieving Date Correction", "action": "Resubmit Date", "next_state": "Pending Supervisor", "allowed": "Employee"},
		{"state": "Pending Supervisor", "action": "Accept & Forward to OM", "next_state": "Pending Operations Manager", "allowed": "All"},
		{"state": "Pending Operations Manager", "action": "Approve", "next_state": "Approved", "allowed": "Operations Manager"}
	]
	for t in transitions_data:
		wf.append("transitions", t)
		
	if not frappe.db.exists("Workflow Action Master", "Accept & Forward to OM"):
		frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": "Accept & Forward to OM"}).insert(ignore_permissions=True)
		
	wf.save(ignore_permissions=True)

	frappe.db.commit()

run()
