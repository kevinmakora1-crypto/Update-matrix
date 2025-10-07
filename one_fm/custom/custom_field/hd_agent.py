def get_hd_agent_custom_fields():
    """Return a dictionary of custom fields for the Employee document."""
    return {
         "HD Agent": [
            {
                "fieldname": "github_api_token",
                "fieldtype": "Password",
                "label": "GitHub API Token",
                "insert_after": "agent_name",
                "description": "GitHub API Token for creating issues on behalf of the user"
            }
        ]
    }