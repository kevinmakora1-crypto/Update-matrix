import frappe
from frappe.utils import getdate

from one_fm.one_fm.doctype.reliever_assignment.reliever_assignment import reassign_responsibilities

def execute():
    august_start = getdate("2025-08-01")
    august_end = getdate("2025-08-31")

    reliever_assignments = frappe.db.get_all("Reliever Assignment", 
        filters={
            "assignment_period_end": ["between", [august_start, august_end]],
            "status": "Transferred"
        },
        pluck="name"
    )

    for obj in reliever_assignments:
        reassign_responsibilities(leave_application=obj)