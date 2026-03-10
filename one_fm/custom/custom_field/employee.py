def get_employee_custom_fields():
    """Return a dictionary of custom fields for the Employee document."""
    return {
        "Employee": [
            {
                "fieldname": "site_supervisor_name",
                "fieldtype": "Data",
                "label": "Site Supervisor Name",
                "insert_after": "site",
                "fetch_from":"site.site_supervisor_name",
                "read_only": 1,
            },
            {
                "fieldname": "project_manager_name",
                "fieldtype": "Data",
                "label": "Project Manager Name",
                "insert_after": "project",
                "fetch_from":"project.project_manager_name",
                "read_only": 1,
            },
            {
                "fieldname": "custom_day_off_preference",
                "fieldtype": "Select",
                "label": "Day Off Preference",
                "insert_after": "leave_policy",
                "options": "\nDay Off\nDay Off OT"
            }
        ]
    }

