import frappe

def execute():
    if frappe.db.exists("Custom Field", "Attendance-is_unscheduled"):

        frappe.db.sql("""
            ALTER TABLE `tabAttendance`
            CHANGE COLUMN `is_unscheduled` `has_no_shift_assignment` INT(1) DEFAULT 0
        """)
        
        frappe.db.sql("""
            UPDATE `tabCustom Field`
            SET fieldname = 'has_no_shift_assignment',
                label = 'Has No Shift Assignment'
            WHERE dt = 'Attendance' AND fieldname = 'is_unscheduled'
        """)
        
        frappe.db.commit()