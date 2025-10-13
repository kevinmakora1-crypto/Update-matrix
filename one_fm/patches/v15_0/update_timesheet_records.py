import frappe
from frappe.utils import getdate
from frappe.workflow.doctype.workflow_action.workflow_action import apply_workflow


def execute():
    the_date = getdate("2025-10-09")
    
    timesheets = frappe.db.get_list(
        "Timesheet",
        filters={
            'workflow_state': 'Pending Approval',
            'start_date': the_date
        },
        fields=['name'],
        pluck='name'
    )
    
    if not timesheets:
        frappe.msgprint(f"No timesheets found for {the_date}")
        return
    
    success_count = 0
    failed_timesheets = []
    
    frappe.msgprint(f"Processing {len(timesheets)} timesheet(s)...")
    
    for ts_name in timesheets:
        try:
            doc = frappe.get_doc("Timesheet", ts_name)
            
            apply_workflow(doc, 'Approve')
            
            doc.reload()

            doc.create_attendance()
            
            success_count += 1
            frappe.db.commit()
            
        except Exception as e:
            frappe.db.rollback()
            failed_timesheets.append(ts_name)
            frappe.log_error(
                title=f"Timesheet Approval Failed: {ts_name}",
                message=f"Timesheet: {ts_name}\nError: {str(e)}\n\n{frappe.get_traceback()}"
            )
    
    msg = f"Completed: {success_count} approved successfully"
    if failed_timesheets:
        msg += f", {len(failed_timesheets)} failed: {', '.join(failed_timesheets)}"
    
    frappe.msgprint(msg)
    print(msg)