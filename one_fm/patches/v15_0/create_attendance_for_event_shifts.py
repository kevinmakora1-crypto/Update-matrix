import frappe
from frappe.utils import get_datetime, time_diff_in_hours

def execute():
    """
    Create attendance records for event-based shifts that don't have attendance yet.
    
    Process:
    1. Get all shift assignments with is_event_based_shift = 1
    2. Filter out those that already have attendance records
    3. Create attendance for remaining shift assignments
    """
    
    shift_assignments = frappe.get_all(
        "Shift Assignment",
        filters={"is_event_based_shift": 1, "docstatus": 1},
        fields=[
            "name", "employee", "employee_name", "start_date", "start_datetime", 
            "end_datetime", "shift", "shift_type", "project", "site", "department",
            "custom_employment_type", "roster_type", "company"
        ]
    )
    
    print(f"Found {len(shift_assignments)} event-based shift assignments")
    
    created_count = 0
    skipped_count = 0
    error_count = 0
    checkin_linked_count = 0
    
    for shift_assignment in shift_assignments:
        try:
            existing_attendance = frappe.db.exists(
                "Attendance",
                {
                    "shift_assignment": shift_assignment.name,
                    "docstatus": ["!=", 2]
                }
            )
            
            if existing_attendance:
                skipped_count += 1
                continue
            
            working_hours = 0
            if shift_assignment.start_datetime and shift_assignment.end_datetime:
                try:
                    start = get_datetime(shift_assignment.start_datetime)
                    end = get_datetime(shift_assignment.end_datetime)
                    working_hours = time_diff_in_hours(end, start)
                except Exception as e:
                    print(f"Error calculating working hours for {shift_assignment.name}: {str(e)}")
            
            attendance = frappe.get_doc({
                "doctype": "Attendance",
                "naming_series": "HR-ATT-.YYYY.-",
                "employee": shift_assignment.employee,
                "employee_name": shift_assignment.employee_name,
                "attendance_date": shift_assignment.start_date,
                "status": "Present",
                "shift_assignment": shift_assignment.name,
                "company": shift_assignment.company or "One Facilities Management",
                "department": shift_assignment.department,
                "operations_shift": shift_assignment.shift,
                "shift": shift_assignment.shift_type,
                "project": shift_assignment.project,
                "site": shift_assignment.site,
                "custom_employment_type": shift_assignment.custom_employment_type,
                "roster_type": shift_assignment.roster_type,
                "working_hours": working_hours,
                "comment": "Checkin but no checkout record found",
                "is_unscheduled": 0,
                "late_entry": 0,
                "early_exit": 0,
                "day_off_ot": 0,
                "modify_half_day_status": 0
            })
            
            attendance.flags.ignore_permissions = True
            attendance.flags.ignore_mandatory = True
            attendance.insert()
            attendance.submit()
            
            created_count += 1
            
            # Link attendance to Employee Checkin records
            try:
                checkins = frappe.get_all(
                    "Employee Checkin",
                    filters={"shift_assignment": shift_assignment.name},
                    fields=["name"]
                )
                
                if checkins:
                    for checkin in checkins:
                        frappe.db.set_value(
                            "Employee Checkin",
                            checkin.name,
                            "attendance",
                            attendance.name,
                            update_modified=False
                        )
                    checkin_linked_count += len(checkins)
                    print(f"Linked {len(checkins)} checkin(s) to attendance {attendance.name}")
                    
            except Exception as checkin_error:
                print(f"Error linking checkins for {shift_assignment.name}: {str(checkin_error)}")
            
            if created_count % 100 == 0:
                frappe.db.commit()
                print(f"Progress: Created {created_count} attendance records")
                
        except Exception as e:
            error_count += 1
            print(f"Error creating attendance for {shift_assignment.name}: {str(e)}")
            frappe.log_error(
                title=f"Attendance Creation Failed - {shift_assignment.name}",
                message=frappe.get_traceback()
            )
            continue
    
    frappe.db.commit()
    
    print(f"""
    Attendance Creation Summary:
    - Total Event-Based Shifts: {len(shift_assignments)}
    - Created: {created_count}
    - Skipped (Already have attendance): {skipped_count}
    - Employee Checkins Linked: {checkin_linked_count}
    - Errors: {error_count}
    """)
    
    print(f"Successfully created {created_count} attendance records")
    print(f"Linked {checkin_linked_count} employee checkin records")
    print(f"Skipped {skipped_count} shifts (already have attendance)")
    if error_count > 0:
        print(f"Failed to create {error_count} attendance records - check error logs")