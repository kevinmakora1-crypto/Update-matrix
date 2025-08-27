from one_fm.setup.setup import delete_custom_fields

def execute():
    custom_fields_to_remove = {
            "Shift Request": [
                {
                    "fieldname": "shift_approver",
                },
                {
                    "fieldname": "custom_shift_approvers",
                }
            ]
        }

    delete_custom_fields(custom_fields_to_remove)