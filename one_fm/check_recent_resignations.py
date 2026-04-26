import frappe

def run():
    resignations = frappe.get_all('Employee Resignation', 
        filters={'creation': ('>', '2026-04-25 13:50:00')}, 
        fields=['name', 'workflow_state', 'creation']
    )
    if not resignations:
        print("NO_RESIGNATIONS_FOUND")
    else:
        for r in resignations:
            print(f"Name: {r.name}, State: {r.workflow_state}, Created: {r.creation}")

run()
