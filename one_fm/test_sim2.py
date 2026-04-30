import frappe
def run():
    payload = {
        "employee_id": "HR-EMP-02438",
        # Notice we use the exact supervisor from user payload
        "supervisor": "Administrator", 
    }
    try:
        from frappe.desk.form.assign_to import add as add_assign
        doc = frappe.new_doc("Employee Resignation")
        doc.append("employees", {"employee": "HR-EMP-02438"})
        doc.workflow_state = "Draft"
        doc.insert(ignore_permissions=True)
        # Fake pending transition
        doc.db_set("workflow_state", "Pending Supervisor")
        add_assign({
            "assign_to": ["Administrator"],
            "doctype": doc.doctype,
            "name": doc.name,
            "description": frappe._("Review Employee Resignation Request")
        })
        print(f"SUCCESS: {doc.name}")
    except Exception as e:
        import traceback
        print("CRASH TRACEBACK:")
        traceback.print_exc()
