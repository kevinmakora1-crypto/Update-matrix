import frappe
def run():
    res = frappe.get_all('Employee Resignation', fields=['name', 'creation', 'owner'], order_by='creation desc', limit=1)
    if res:
        doc = frappe.get_doc('Employee Resignation', res[0].name)
        print(f"RESIGNATION: {doc.name}")
        for emp in doc.employees:
            print(f"  - Employee: {emp.employee} ({frappe.db.get_value('Employee', emp.employee, 'employee_name')})")
            print(f"  - Letter: {emp.resignation_letter}")
run()
