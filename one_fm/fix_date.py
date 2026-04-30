import frappe

def execute():
    try:
        adj = frappe.get_doc('Employee Resignation Date Adjustment', 'HR-ERDA-2026-04-0001')
        print(f"Found Adjustment: {adj.name}")
        
        # 1. Update Employee Resignation parent Doc
        if adj.employee_resignation:
            resignation = frappe.get_doc("Employee Resignation", adj.employee_resignation)
            resignation.db_set("relieving_date", adj.extended_relieving_date)
            print(f"Updated resignation {resignation.name} relieving_date to {adj.extended_relieving_date}")
            
            # 2. Update all Employees natively linked to the parent resignation batch!
            if adj.get("employees"):
                for row in adj.employees:
                    if row.employee:
                        frappe.db.set_value("Employee", row.employee, "relieving_date", adj.extended_relieving_date)
                        print(f"Updated employee {row.employee} relieving_date")

            # 3. Update Project Manpower Request Deployment Date securely
            pmr_name = frappe.db.get_value("Project Manpower Request", {"employee_resignation": adj.employee_resignation}, "name")
            if pmr_name:
                pmr = frappe.get_doc("Project Manpower Request", pmr_name)
                from frappe.utils import add_days
                ojt = pmr.ojt_days or 0
                revised_deployment_date = add_days(adj.extended_relieving_date, -ojt)
                pmr.db_set("deployment_date", revised_deployment_date)
                print(f"Updated PMR {pmr_name} deployment_date to {revised_deployment_date}")

        frappe.db.commit()
    except Exception as e:
        print(f"Error: {e}")
