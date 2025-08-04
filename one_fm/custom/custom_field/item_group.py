def get_item_group_custom_fields():
    return {
        "Item Group": [
            {
                "fieldname": "item_group_code",
                "fieldtype": "Read Only",
                "insert_after": "gs",
                "label": "Item Group Code"
            },
            {
                "fieldname": "one_fm_item_group_abbr",
                "fieldtype": "Data",
                "insert_after": "item_group_name",
                "label": "Item Group Abbreviation",
                "translatable": 1
            },
            {
                "fieldname": "one_fm_item_group_descriptions_sb",
                "fieldtype": "Section Break",
                "insert_after": "asset_category",
                "label": "Descriptions"
            },
            {
                "fieldname": "one_fm_item_group_descriptions",
                "fieldtype": "Table",
                "insert_after": "one_fm_item_group_descriptions_sb"
            }
        ]
    }
