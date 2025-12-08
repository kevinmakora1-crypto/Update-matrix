def get_workflow_document_state_custom_fields():
    return {
        "Workflow Document State": [
            {
                "fieldname": "style",
                "fieldtype": "Data",
                "label": "Style",
                "insert_after": "update_value",
                "fetch_from": "state.style"
            }
        ]
    }
