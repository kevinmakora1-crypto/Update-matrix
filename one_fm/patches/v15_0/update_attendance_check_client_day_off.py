import frappe


def execute():
    pending_checks = frappe.db.get_list(
        "Attendance Check",
        filters={"workflow_state": "Pending Approval"},
        fields=["date", "employee", "name"],
    )

    for check in pending_checks:
        employee = check["employee"]
        date = check["date"]

        employee_schedule = frappe.db.get_value(
            "Employee Schedule",
            {
                "employee": employee,
                "employee_availability": "Client Day Off",
                "date": date
            },
            "name"
        )

        if not employee_schedule:
            continue

       
        existing_attendance = frappe.db.get_value(
            "Attendance",
            {"employee": employee, "attendance_date": date},
            ["name", "status", "roster_type"],
            as_dict=True
        )

        if existing_attendance:
            if existing_attendance.status == "Absent" and existing_attendance.roster_type == "Basic":
                comment = f"Employee Schedule - {employee_schedule}"
                frappe.db.sql("""
                    UPDATE `tabAttendance`
                    SET status = %s,
                        comment = %s
                    WHERE name = %s
                """, ("Client Day Off", comment, existing_attendance.name))

            else:
                pass
        else: 
            attendance = frappe.get_doc({
                "doctype": "Attendance",
                "attendance_date": date,
                "status": "Client Day Off",
                "employee": employee,
                "comment": f"Employee Schedule - {employee_schedule}"
            })
            attendance.insert()
            attendance.submit()

        
        frappe.db.set_value(
            "Attendance Check",
            check["name"],
            {
                "workflow_state": "Approved",
                "docstatus": 1,
                "attendance_status": "Day Off"
            }
        )

    frappe.db.commit()

