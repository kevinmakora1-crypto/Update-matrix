"""
Patch: Setup Interview Console Custom Fields & DocTypes
Run: bench --site site_name run-patch one_fm.patches.v15_0.setup_interview_console
"""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    # --- 1. Create child doctype: Interview Evaluation Detail ---
    if not frappe.db.exists("DocType", "Interview Evaluation Detail"):
        try:
            doc = frappe.get_doc({
                "doctype": "DocType",
                "name": "Interview Evaluation Detail",
                "module": "One Fm",
                "custom": 1,
                "istable": 1,
                "editable_grid": 1,
                "fields": [
                    {"fieldname": "category", "fieldtype": "Data", "label": "Category",
                     "in_list_view": 1, "columns": 2},
                    {"fieldname": "question", "fieldtype": "Small Text", "label": "Question",
                     "in_list_view": 1, "columns": 4},
                    {"fieldname": "weight", "fieldtype": "Float", "label": "Weight",
                     "in_list_view": 1, "columns": 1, "precision": 2},
                    {"fieldname": "rating", "fieldtype": "Int", "label": "Rating",
                     "in_list_view": 1, "columns": 1, "description": "Score 1-5"},
                    {"fieldname": "max_rating", "fieldtype": "Int", "label": "Max Rating",
                     "in_list_view": 1, "columns": 1, "default": "5"},
                ]
            })
            doc.insert(ignore_permissions=True)
            print("Created DocType: Interview Evaluation Detail")
        except frappe.DuplicateEntryError:
            pass

    # --- 2. Custom Fields on Interview Feedback ---
    create_custom_fields({
        "Interview Feedback": [
            {
                "fieldname": "custom_evaluation_criteria",
                "fieldtype": "Table",
                "label": "Evaluation Criteria",
                "options": "Interview Evaluation Detail",
                "insert_after": "feedback",
                "read_only": 1,
            },
            {
                "fieldname": "custom_remarks",
                "fieldtype": "Small Text",
                "label": "Remarks",
                "insert_after": "custom_evaluation_criteria",
            },
        ]
    }, update=True)

    # --- 3. Custom Fields on Interview ---
    create_custom_fields({
        "Interview": [
            {
                "fieldname": "interview_summary_render",
                "fieldtype": "HTML",
                "label": "Interview Summary",
                "insert_after": "interview_details",
            },
            {
                "fieldname": "total_interview_score",
                "fieldtype": "Float",
                "label": "Total Score",
                "insert_after": "average_rating",
            },
            {
                "fieldname": "custom_hiring_method",
                "fieldtype": "Data",
                "label": "Hiring Method",
                "insert_after": "designation",
            },
        ]
    }, update=True)

    print("Interview Console setup complete!")
