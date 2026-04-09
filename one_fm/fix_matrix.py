import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def run():
    frappe.init(site="onefm.local")
    frappe.connect()

    # 1. Update the Doctype fields (Drop category & weight, make question readonly)
    dt = frappe.get_doc("DocType", "Interview Matrix Question")
    # clear old fields
    dt.fields = []
    
    new_fields = [
        {"fieldname": "question", "fieldtype": "Small Text", "label": "Question", "in_list_view": 1, "read_only": 1, "reqd": 1, "columns": 2},
        {"fieldname": "score_5", "fieldtype": "Small Text", "label": "Score 5 (Excellent)", "columns": 2},
        {"fieldname": "score_4", "fieldtype": "Small Text", "label": "Score 4 (Good)", "columns": 2},
        {"fieldname": "score_3", "fieldtype": "Small Text", "label": "Score 3 (Average)", "columns": 2},
        {"fieldname": "score_2", "fieldtype": "Small Text", "label": "Score 2 (Poor)", "columns": 2},
        {"fieldname": "score_1", "fieldtype": "Small Text", "label": "Score 1 (Very Poor)", "columns": 2}
    ]
    
    for f in new_fields:
        dt.append("fields", f)
        
    dt.save(ignore_permissions=True)

    # 2. Modify Custom Field position to be at the very bottom
    # We find our custom field
    cf_sb = frappe.get_doc("Custom Field", "Interview Round-interview_matrix_sb")
    cf_sb.insert_after = "interview_question" # ensure section break is also at the bottom
    cf_sb.save(ignore_permissions=True)

    cf = frappe.get_doc("Custom Field", "Interview Round-interview_matrix")
    cf.insert_after = "interview_matrix_sb"
    cf.save(ignore_permissions=True)

    frappe.db.commit()
    print("Fixed matrix layout")
