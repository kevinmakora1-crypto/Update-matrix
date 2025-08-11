import frappe
from frappe.utils import getdate, today

from one_fm.one_fm.doctype.reliever_assignment.reliever_assignment import assign_responsibilities
from one_fm.utils import fetch_leave_types_update_employee_status


def execute():
    the_date = getdate("21-07-2025") 
    
    reliever_assignment_names = frappe.db.get_all(
        "Reliever Assignment",
        filters={"creation": [">=", the_date]}, 
        pluck="name"
    )

    leave_applications = frappe.db.get_all(
        'Leave Application',
        filters={
            "leave_type": ["IN", fetch_leave_types_update_employee_status()],
            "name": ["NOT IN", reliever_assignment_names] if reliever_assignment_names else [],
            "status": "Approved",
            "creation": [">=", the_date],
            "custom_reliever_": ["is", "set"],
            "to_date": [">=", today()],
        },
        fields=['employee', "employee_name", "employee.status", 'custom_reliever_', 'name'],
        distinct=True,
        order_by="employee, creation desc"
    )

    
    if not leave_applications:
        frappe.logger().info("No leave applications found matching criteria")
        return
    
    for leave_app in leave_applications:
        name = leave_app.get('name')
        employee_status = leave_app.get('status')

        try:
            if employee_status == "Vacation":
                assign_responsibilities(leave_application=name)
                
        except Exception as e:
            frappe.log_error(f"Error assigning responsibilities for {name}: {str(e)}")
        else:
            continue

    
    frappe.db.commit()