import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    # Check if the field already exists
    if not frappe.db.exists('Custom Field', {'dt': 'Interview Round', 'fieldname': 'one_fm_nationality'}):
        create_custom_field('Interview Round', {
            'fieldname': 'one_fm_nationality',
            'label': 'Nationality',
            'fieldtype': 'Link',
            'options': 'Nationality',
            'insert_after': 'designation',
            'module': 'One Fm'
        })
        print("Successfully added one_fm_nationality to Interview Round.")
    else:
        print("Field already exists.")
