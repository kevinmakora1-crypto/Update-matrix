import frappe
from frappe.utils import getdate
from frappe.workflow.doctype.workflow_action.workflow_action import apply_workflow


def execute():
    the_date = getdate("2025-10-09")
    timesheets = frappe.db.get_list("Timesheet", {'workflow_state':'Pending Approval',
       "start_date": the_date})

    for i in timesheets:
        try:
            apply_workflow(frappe.get_doc("Timesheet", i.name), 'Approve')
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Timesheet Marking")

        doc = frappe.get_doc("Timesheet", i.name)
        doc.create_attendance()


    frappe.db.commit()
