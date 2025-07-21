def get_todo_custom_fields():
    """Return a dictionary of custom fields for the Employee document."""
    return {
         "ToDo": [
            {
                "fieldname": "notify_allocated_to_via_email",
                "fieldtype": "Check",
                "label": "Notify Allocated To Via Email",
                "insert_after": "allocated_to",
                "allow_in_quick_entry": 1
            },
        ]
    }
