def get_hr_settings_custom_fields():
    return {
        "HR Settings": [
            {
                "fieldname": "custom_hr_manager",
                "fieldtype": "Link",
                "insert_after": "retirement_age",
                "label": "HR Manager",
                "options": "User",
                "description": "User ID of current HR Manager."
            },
            {
                "fieldname": "payroll_notifications_email",
                "fieldtype": "Data",
                "insert_after": "payroll_settings",
                "label": "Payroll Notifications Email",
                "description": "All payroll related notifications will be forwarded to this email id.",
                "translatable": 1
            }
        ]
    }
