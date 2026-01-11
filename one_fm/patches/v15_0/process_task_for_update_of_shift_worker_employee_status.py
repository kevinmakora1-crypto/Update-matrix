from one_fm.utils import create_process_task

def execute():
    create_process_task(
        process_name= "Others",
        erp_document= "Leave Application",
        task_description= "Daily automated task that checks employees returning from annual leave today and updates " \
        "their status based on accommodation check-ins (for shift workers) or automatically sets to Active (for non-shift workers). ",
        task_type= "Routine",
        is_routine_task= 1,
        frequency= "Cron",
        cron_format= "0 1 * * *",
        is_automated= 1,
        method= "one_fm.overrides.leave_application.update_employee_status_after_leave"
    )

