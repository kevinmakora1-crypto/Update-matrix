"""
Patch: Setup Interview Console Custom Fields & DocTypes
Run on production: bench --site site_name run-patch one_fm.patches.v15_0.setup_interview_console
"""
import frappe


def execute():
    # --- 1. Create child doctype: Interview Evaluation Detail ---
    if not frappe.db.exists("DocType", "Interview Evaluation Detail"):
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
        print("✅ Created DocType: Interview Evaluation Detail")

        # Create DB table
        frappe.db.sql("""CREATE TABLE IF NOT EXISTS `tabInterview Evaluation Detail` (
            name varchar(140) NOT NULL,
            creation datetime(6) DEFAULT NULL,
            modified datetime(6) DEFAULT NULL,
            modified_by varchar(140) DEFAULT NULL,
            owner varchar(140) DEFAULT NULL,
            docstatus int(1) NOT NULL DEFAULT 0,
            parent varchar(140) DEFAULT NULL,
            parentfield varchar(140) DEFAULT NULL,
            parenttype varchar(140) DEFAULT NULL,
            idx int(8) NOT NULL DEFAULT 0,
            category varchar(140) DEFAULT NULL,
            question text DEFAULT NULL,
            weight decimal(18,6) DEFAULT 0.000000,
            rating int(11) DEFAULT 0,
            max_rating int(11) DEFAULT 5,
            PRIMARY KEY (name),
            KEY parent (parent)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""")
        print("✅ Created DB table: tabInterview Evaluation Detail")

    # --- 2. Custom Fields on Interview Feedback ---
    feedback_fields = [
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

    for field in feedback_fields:
        if not frappe.db.exists("Custom Field", {"dt": "Interview Feedback", "fieldname": field["fieldname"]}):
            cf = frappe.get_doc({"doctype": "Custom Field", "dt": "Interview Feedback", **field})
            cf.insert(ignore_permissions=True)
            print(f"✅ Created Custom Field: Interview Feedback.{field['fieldname']}")

    # --- 3. Custom Fields on Interview ---
    interview_fields = [
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

    for field in interview_fields:
        if not frappe.db.exists("Custom Field", {"dt": "Interview", "fieldname": field["fieldname"]}):
            cf = frappe.get_doc({"doctype": "Custom Field", "dt": "Interview", **field})
            cf.insert(ignore_permissions=True)
            print(f"✅ Created Custom Field: Interview.{field['fieldname']}")

    frappe.db.commit()
    print("\n🎉 Interview Console setup complete!")
