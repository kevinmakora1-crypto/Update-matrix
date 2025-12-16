import frappe
from one_fm.custom.custom_field.workflow_document_state import get_workflow_document_state_custom_fields

def execute():
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    create_custom_fields(get_workflow_document_state_custom_fields())
