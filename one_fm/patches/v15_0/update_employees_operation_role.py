import frappe

@frappe.whitelist()
def execute():
    shift_employees = frappe.get_all("Employee",fields=['name'],filters={'shift_working':1,'status':'Active'})
    employees_name = [employee_name['name'] for employee_name in shift_employees]
    if not employees_name:
        return []
    query = """
        SELECT es.employee,es.shift,es.operations_role
        FROM `tabEmployee Schedule` as es
        WHERE es.roster_type = 'Basic'
        AND es.employee_availability = 'Working'
        AND es.employee IN %(employee_names)s
        AND es.date = (
            SELECT MAX(date)
            FROM `tabEmployee Schedule` AS sub
            WHERE sub.employee = es.employee
        )
    """
    schedules = frappe.db.sql(query, {"employee_names": employees_name}, as_dict=True)
    schedule_map = {schedule['employee']: schedule for schedule in schedules}

    for employee in employees_name:
        update_operation_role = frappe.get_doc('Employee',employee)
        schedule = schedule_map.get(employee)
        if schedule and update_operation_role.shift and update_operation_role.shift == schedule['shift']:
            update_operation_role.custom_operations_role_allocation = schedule['operations_role']
            update_operation_role.save(ignore_permissions=True)
    frappe.db.commit()
