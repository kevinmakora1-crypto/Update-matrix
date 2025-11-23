from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_fields = {
        "Employee Checkin": [
            {
                "fieldname": "source",
                "fieldtype": "Select",
                "insert_after": "employee_checkin_issue",
                "label": "Source",
                "options": "\nMobile App\nMobile Web\nCheck-in Form\nFrappe Page\nAttendance Check",
                "default": "Check-in Form",
                "translatable": 1
            }
        ]
    }
    create_custom_fields(custom_fields)