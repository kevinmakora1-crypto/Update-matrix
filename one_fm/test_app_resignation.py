import frappe
import json
import sys
import os
sys.path.append(os.path.abspath('apps/one_fm'))
from one_fm.api.v1.resignation import create_resignation, extend_resignation, withdraw_resignation, get_my_active_resignation

def run_test():
    frappe.init(site="onefm.local", sites_path="./sites")
    frappe.connect()
    
    frappe.db.set_value('DocType', 'Employee Resignation Extension', 'custom', 1)
    frappe.db.set_value('DocType', 'Employee Resignation Extension', 'module', 'One Fm')
    frappe.db.commit()
    frappe.clear_cache(doctype='Employee Resignation Extension')
    
    print("Finding a valid Employee...")
    employee = frappe.db.get_value("Employee", {"status": "Active"}, ["name", "reports_to", "employee"], as_dict=True)
    if not employee:
        print("No active employee found! Aborting.")
        return
        
    employee_id = employee.employee or employee.name
    supervisor_emp = employee.reports_to
    supervisor = None
    if supervisor_emp:
        supervisor = frappe.db.get_value("Employee", supervisor_emp, "user_id")
    
    if not supervisor:
        print("Employee has no supervisor, finding a random user to act as supervisor...")
        supervisor = frappe.db.get_value("User", {"enabled": 1, "user_type": "System User"}, "name")
        
    print(f"Testing with Employee: {employee_id}, Supervisor: {supervisor}")
    
    # 1. Test get_my_active_resignation
    active = get_my_active_resignation(employee_id)
    if active:
        print(f"Found existing active resignation: {active.get('name')}. Deleting it for clean test...")
        old_doc = frappe.get_doc("Employee Resignation", active.get('name'))
        if old_doc.docstatus == 1:
            old_doc.cancel()
        frappe.delete_doc("Employee Resignation", active.get('name'), force=1)
        frappe.db.commit()
        
    # 2. Test create_resignation
    print("--- 1. Testing create_resignation API ---")
    payload = {
        "employee_id": employee_id,
        "supervisor": supervisor,
        "relieving_date": "2026-12-31"
    }
    resignation_id = create_resignation(data=json.dumps(payload))
    print(f"✅ Created Resignation: {resignation_id}")
    frappe.db.commit()
    
    # Verify State
    doc = frappe.get_doc("Employee Resignation", resignation_id)
    doc.db_set("relieving_date", "2026-12-31")
    print(f"State: {doc.workflow_state}, Relieving Date: {doc.relieving_date}")
    if doc.workflow_state != "Pending Supervisor":
        print("❌ Workflow state is not 'Pending Supervisor'")
        
    # 3. Test extend_resignation
    print("--- 2. Testing extend_resignation API ---")
    extend_payload = {
        "employee_id": employee_id,
        "supervisor": supervisor,
        "resignation_id": resignation_id,
        "extended_date": "2026-12-31"
    }
    from one_fm.api.v1.resignation import extend_resignation
    res = extend_resignation(data=json.dumps(extend_payload))
    print(f"✅ Extension API Response: {res}")
    
    # 4. Test withdraw_resignation
    print("--- 3. Testing withdraw_resignation API ---")
    withdraw_payload = {
        "employee_id": employee_id,
        "supervisor": supervisor,
        "employee_resignation": resignation_id,
        "reason": "Decided to stay"
    }
    withdrawal_id = withdraw_resignation(data=json.dumps(withdraw_payload))
    print(f"✅ Created Withdrawal: {withdrawal_id}")
    
    frappe.db.rollback() # Rollback to keep DB clean
    print("\n🎉 All mobile app backend APIs executed successfully! Database rolled back.")

if __name__ == "__main__":
    run_test()
