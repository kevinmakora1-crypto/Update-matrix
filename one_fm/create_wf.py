import frappe

def execute():
    # Find existing workflow for Withdrawal
    wf_name = frappe.db.get_value("Workflow", {"document_type": "Employee Resignation Withdrawal"}, "name")
    if not wf_name:
        print("No withdrawal workflow found to copy.")
        return
        
    doc = frappe.get_doc("Workflow", wf_name)
    if frappe.db.exists("Workflow", {"document_type": "Employee Resignation Extension"}):
        print("Extension workflow already exists.")
        return
        
    new_doc = frappe.copy_doc(doc)
    new_doc.workflow_name = "Employee Resignation Extension Workflow"
    new_doc.document_type = "Employee Resignation Extension"
    
    # We must reset states safely
    for state in new_doc.states:
        pass # Identical flow
        
    new_doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print("Created Workflow!")
    
