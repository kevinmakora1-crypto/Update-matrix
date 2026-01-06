from one_fm.utils import create_process_task

def execute():
    create_process_task(
        process_name= "Others",
        erp_document= "Demand Letter",
        task_description= "Demand Letter Expiry Notification",
        task_type= "Routine",
        is_routine_task= 1,
        frequency= "Daily",
        is_automated= 1,
        method= "one_fm.one_fm.doctype.demand_letter.demand_letter.inform_demand_letter_validity_expiry"
    )