import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from one_fm.custom.custom_field.interview_feedback import get_interview_feedback_custom_fields

def run():
    custom_fields = get_interview_feedback_custom_fields()
    create_custom_fields(custom_fields)
    frappe.db.commit()
    print("Custom fields successfully synced!")
