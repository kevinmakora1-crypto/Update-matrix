def get_hd_ticket_custom_fields():
    """Return a dictionary of custom fields for the Employee document."""
    return {
         "HD Ticket": [
            {
                "fieldname": "custom_process",
                "fieldtype": "Link",
                "label": "Process",
                "insert_after": "cb00",
                "reqd": 1,
                "default": "Others", 
                "options": "Process"
                
            },
        ]
    }

