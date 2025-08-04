def get_issue_custom_fields():
    return {
        "Issue": [
            {
                "fieldname": "pivotal_tracker",
                "fieldtype": "Data",
                "insert_after": "content_type",
                "label": "Pivotal Tracker",
                "read_only": 1,
                "translatable": 1
            },
            {
                "fieldname": "department",
                "fieldtype": "Link",
                "insert_after": "priority",
                "label": "Department",
                "options": "Department"
            },
            {
                "fieldname": "communication_medium",
                "fieldtype": "Select",
                "insert_after": "raised_by",
                "label": "Communication Medium",
                "options": "\nEmail\nWhatsApp\nMobile App\nSystem",
                "in_standard_filter": 1
            }
        ]
    }
