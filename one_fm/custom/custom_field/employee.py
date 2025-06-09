def get_employee_custom_fields():
    """Return a dictionary of custom fields for the Employee document."""
    return {
        "Employee": [
            {
                "fieldname": "custom_site_supervisor_name",
                "owner":"Administrator",
                "fieldtype": "Data",
                "label": "Site Manager",
                "insert_after": "site",
                "fetch_from":"site.account_supervisor_name",
                "read_only": 1,
            },
            {
                "fieldname": "project_manager_name",
                "owner":"Administrator",
                "fieldtype": "Data",
                "label": "Project Manager Name",
                "insert_after": "project",
                "fetch_from":"project.manager_name",
                "read_only": 1,
                }
        ]
    }

