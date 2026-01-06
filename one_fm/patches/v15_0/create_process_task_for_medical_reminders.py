
from one_fm.utils import create_process_task

def execute():
    create_process_task(
		process_name= "Others",
        erp_document= "Medical Appointment",
        task_description= "Medical Appointment Transportation",
        task_type= "Routine",
		is_routine_task= 1,
        frequency= "Cron",
        cron_format= "0 9 * * *",
		is_automated= 1,
		method= "one_fm.grd.doctype.medical_appointment.medical_appointment.send_medical_appointment_reminders"
	)
