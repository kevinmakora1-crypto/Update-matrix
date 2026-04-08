import os
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def setup(site=None):
    site = site or os.environ.get("FRAPPE_SITE")
    connected_here = False
    active_site = getattr(frappe.local, "site", None)
    if site:
        frappe.init(site=site)
        frappe.connect()
        connected_here = True
    elif not active_site:
        raise RuntimeError(
            "setup() must be run within an active Frappe site context or be passed a site argument."
        )
    try:
        doc_name = "Interview Matrix Question"
        if not frappe.db.exists("DocType", doc_name):
            doc = frappe.new_doc("DocType")
            doc.name = doc_name
            doc.module = "One Fm"
            doc.custom = 1
            doc.istable = 1
            doc.editable_grid = 1
            fields = [
                {"fieldname": "category", "fieldtype": "Data", "label": "Category", "in_list_view": 1},
                {"fieldname": "question", "fieldtype": "Text", "label": "Question", "in_list_view": 1, "reqd": 1},
                {"fieldname": "weight", "fieldtype": "Int", "label": "Weight", "in_list_view": 1},
                {"fieldname": "score_5", "fieldtype": "Text", "label": "Score 5 (Excellent)"},
                {"fieldname": "score_4", "fieldtype": "Text", "label": "Score 4 (Good)"},
                {"fieldname": "score_3", "fieldtype": "Text", "label": "Score 3 (Average)"},
                {"fieldname": "score_2", "fieldtype": "Text", "label": "Score 2 (Poor)"},
                {"fieldname": "score_1", "fieldtype": "Text", "label": "Score 1 (Very Poor)"}
            ]
            doc.set("fields", [])
            for f in fields:
                doc.append("fields", f)
            doc.insert(ignore_permissions=True)
            print(f"Created Doctype {doc_name}")
        custom_fields = {
            "Interview Round": [
                {
                    "fieldname": "interview_matrix_sb",
                    "fieldtype": "Section Break",
                    "label": "Evaluation Matrix Config"
                },
                {
                    "fieldname": "interview_matrix",
                    "fieldtype": "Table",
                    "label": "Interview Questions Setup",
                    "options": "Interview Matrix Question"
                }
            ]
        }
        create_custom_fields(custom_fields)
        frappe.db.commit()
        print("Added custom fields to Interview Round")
    finally:
        if connected_here:
            frappe.destroy()
