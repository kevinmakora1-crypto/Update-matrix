"""
Patch: Setup Interview Console Custom Fields
Adds custom fields on Interview Feedback and Interview doctypes
needed by the Interview Console page.
"""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    # --- Custom Fields on Interview Feedback ---
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

    # --- Custom Fields on Interview ---
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
        ]
    }, update=True)

    print("Interview Console custom fields installed!")
