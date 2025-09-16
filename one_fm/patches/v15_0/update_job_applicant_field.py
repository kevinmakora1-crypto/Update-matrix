from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from one_fm.custom.custom_field.job_applicant import get_job_applicant_custom_fields

def execute():
	create_custom_fields(get_job_applicant_custom_fields())