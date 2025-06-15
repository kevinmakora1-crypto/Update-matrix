def get_attendance_custom_fields():
    return {
        "Attendance":[
            {
                "fieldname": "is_unscheduled",
                "fieldtype": "Check",
                "insert_after": "comment",
                "label": "Is Unscheduled"
            }
        ]
    }