import frappe
import json

def run():
    # 1. Check Workflow states
    states = frappe.get_all("Workflow State", fields=["name", "workflow_state"])
    print(f"States: {states}")
    
    # 2. Check Workflow
    wf = frappe.get_all("Workflow", filters={"document_type": "Employee Resignation"}, fields=["name"])
    if not wf:
        print("No Workflow found for Employee Resignation")
        return
    
    wf_name = wf[0].name
    print(f"Workflow Name: {wf_name}")
    
    # 3. Check transitions
    transitions = frappe.get_all("Workflow Transition", filters={"parent": wf_name}, fields=["state", "action", "next_state", "send_email_alert"])
    print(f"Transitions: {transitions}")

run()
