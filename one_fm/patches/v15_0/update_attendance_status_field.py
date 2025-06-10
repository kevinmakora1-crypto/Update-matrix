# file: one_fm/patches/v15_10/add_attendance_status_options.py
import frappe

def execute():
    """
    Adds / updates the Property Setter that controls
    Attendance.status selectable options.
    """
    prop_setter_name = "Attendance-status-options"
    options = (
        "Present\n"
        "Absent\n"
        "On Leave\n"
        "Half Day\n"
        "Work From Home\n"
        "Day Off\n"
        "Client Day Off\n"
        "Holiday\n"
        "On Hold"
    )

    ps = frappe.db.exists("Property Setter", prop_setter_name)
    if ps:
        frappe.db.set_value(
            "Property Setter",
            prop_setter_name,
            "value",
            options,
        )
    else:
        frappe.get_doc({
            "doctype": "Property Setter",
            "name": prop_setter_name,
            "doctype_or_field": "DocField",
            "doc_type": "Attendance",
            "field_name": "status",
            "property": "options",
            "property_type": "Select",
            "value": options,
        }).insert(ignore_permissions=True)


