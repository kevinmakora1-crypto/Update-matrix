import frappe

@frappe.whitelist()
def execute():
    shift_employees = frappe.get_all("Employee",fields=['name'],filters={'shift_working':1,'status':'Active'})
    employees_name = [employee_name['name'] for employee_name in shift_employees]
    if not employees_name:
        return []
    query = """
        SELECT *
        FROM `tabEmployee Schedule`
        WHERE roster_type = 'Basic'
        AND employee_availability = 'Working'
        AND employee IN %(employee_names)s
        AND date = (
            SELECT MAX(date)
            FROM `tabEmployee Schedule` AS sub
            WHERE sub.employee = `tabEmployee Schedule`.employee
        )
    """
    schedules = frappe.db.sql(query, {"employee_names": employees_name}, as_dict=True)

    combined_data = [{
        'employee':employee_name,
        'schedule':next((schedule for schedule in schedules if schedule.employee==employee_name), None)
    } for employee_name in employees_name]

    for employee in combined_data:
        update_operation_role = frappe.get_doc('Employee',employee['employee'])
        update_operation_role.custom_operations_role_allocation = employee['schedule']['operations_role']
        update_operation_role.save(ignore_permissions=True)
        frappe.db.commit()
