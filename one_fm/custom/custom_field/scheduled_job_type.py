def get_scheduled_job_type_custom_fields():
    """Return a dictionary of custom fields for the Employee document."""
    return {
         "Scheduled Job Type": [
            {
                "fieldname": "process_task",
                "fieldtype": "Link",
                "label": "Process Task",
                "insert_after": "server_script",
                "options": "Process Task",
                "read_only": 1
            },
        ]
    }
