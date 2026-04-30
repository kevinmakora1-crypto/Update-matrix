import frappe, json
from frappe.modules.import_file import import_file_by_path

def execute():
    try:
        if frappe.db.exists("Workflow", "Employee Resignation"):
            frappe.delete_doc("Workflow", "Employee Resignation", force=1)
        if frappe.db.exists("Workflow", "Employee Resignation Withdrawal"):
            frappe.delete_doc("Workflow", "Employee Resignation Withdrawal", force=1)
            
        states = ["Draft", "Pending Supervisor", "Pending Operations Manager", "Approved", "Withdrawn", "Accepted by Supervisor", "Rejected By Supervisor", "Rejected"]
        styles = {"Draft": "Primary", "Pending Supervisor": "Warning", "Pending Operations Manager": "Warning", "Approved": "Success", "Withdrawn": "Danger", "Accepted by Supervisor": "Warning", "Rejected By Supervisor": "", "Rejected": "Inverse"}
        
        for state in states:
            if frappe.db.exists("Workflow State", state):
                continue
            
            frappe.db.sql(f"DELETE FROM `tabWorkflow State` WHERE workflow_state_name = '{state}'")
            
            doc = frappe.new_doc("Workflow State")
            doc.workflow_state_name = state
            doc.style = styles[state]
            doc.insert(ignore_permissions=True, ignore_mandatory=True)
            
        path1 = "/Users/kevinmakora/.gemini/antigravity/scratch/frappe-bench/apps/one_fm/one_fm/custom/workflow/employee_resignation.json"
        path2 = "/Users/kevinmakora/.gemini/antigravity/scratch/frappe-bench/apps/one_fm/one_fm/custom/workflow/employee_resignation_withdrawal.json"
        
        import_file_by_path(path1, force=True)
        import_file_by_path(path2, force=True)
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        raise e
