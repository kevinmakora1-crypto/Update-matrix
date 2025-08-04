def get_item_custom_fields():
    return {
        "Item": [
            {
                "fieldname": "hub_sync_id",
                "fieldtype": "Data",
                "insert_after": "workflow_state",
                "label": "Hub Sync ID",
                "hidden": 1,
                "read_only": 1,
                "unique": 1,
                "no_copy": 1
            },
            {
                "fieldname": "description1",
                "fieldtype": "Data",
                "insert_after": "item_descriptions",
                "label": "Description1",
                "hidden": 1
            },
            {
                "fieldname": "description2",
                "fieldtype": "Data",
                "insert_after": "description1",
                "label": "Description2",
                "hidden": 1
            }
        ]
    }
