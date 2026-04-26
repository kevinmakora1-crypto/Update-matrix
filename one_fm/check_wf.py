import frappe
from pprint import pprint

def execute():
    wf_name = frappe.get_active_workflow("Employee Resignation")
    print(f"Workflow: {wf_name}")
    transitions = frappe.get_all("Workflow Transition", filters={"parent": wf_name}, fields=["state", "action", "next_state"])
    for t in transitions:
        print(t)
