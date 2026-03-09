import frappe
from one_fm.setup.assignment_rule import create_assignment_rule, get_assignment_rule_json_file
from one_fm.utils import create_process_task


def execute():
    # Create the Process Task first (single-file flow like ERF bulk patch)
    process_task = create_process_task(
        process_name="Requisition Process",
        erp_document="Assignment Rule",
        task_description=(
            "Updating the Warehouse Supervisor's user's ID in Assignment Rule for RFM upon approval."
        ),
        employee="HR-EMP-02117",
        process_owner=None,
        business_analyst=None,
        task_type="Repetitive",
        is_routine_task=0,
        is_automated=0,
        method="",
    )

    # Load assignment rule data from JSON
    assignment_rule_data = get_assignment_rule_json_file(
        "assign_warehouse_supervisor_upon_approval.json"
    )

    # Enrich with employee details from the created Process Task
    process_task_name = None
    if process_task:
        process_task_name = process_task.name
        if process_task.employee:
            employee_data = frappe.db.get_value(
                "Employee",
                process_task.employee,
                ["employee_name", "user_id", "department"],
                as_dict=True,
            )
            if employee_data:
                assignment_rule_data["employee_name"] = employee_data.employee_name
                assignment_rule_data["employee_user"] = employee_data.user_id
                assignment_rule_data["department"] = employee_data.department

    # Create/update Assignment Rule linked to Process Task
    create_assignment_rule(assignment_rule_data, process_task_name)
