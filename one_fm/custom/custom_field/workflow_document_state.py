def get_workflow_document_state_custom_fields():
    return {
        "Workflow Document State": [
            {
                "fieldname": "style",
                "fieldtype": "Data",
                "label": "Style",
                "insert_after": "update_value",
                "fetch_from": "state.style"
            },
            {
                "label": "Banner Message",
                "fieldname": "banner_message",
                "fieldtype": "Small Text",
                "insert_after": "message",
                "description": "The message here will be displayed when a document in this workflow state is opened.",
            }
        ]
    }
