from one_fm.utils import create_process_task

def execute():
    create_process_task(
        process_name= "Others",
        erp_document= "Agency",
        task_description= "Agency License Expiry Notification",
        task_type= "Routine",
        is_routine_task= 1,
        frequency= "Daily",
        is_automated= 1,
        method= "one_fm.one_fm.doctype.agency.agency.inform_license_expiry"
    )

    create_process_task(
        process_name= "Others",
        erp_document= "Agency",
        task_description= "Agency Inactive on License Expiry",
        task_type= "Routine",
        is_routine_task= 1,
        frequency= "Daily",
        is_automated= 1,
        method= "one_fm.one_fm.doctype.agency.agency.inactive_agency_on_license_expiry"
    )