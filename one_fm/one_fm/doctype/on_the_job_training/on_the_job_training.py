# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt

from datetime import timedelta

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, add_days, get_datetime



class OntheJobTraining(Document):
    def validate(self):
        if self.start_date and self.end_date:
            if getdate(self.end_date) < getdate(self.start_date):
                frappe.throw(_("End Date cannot be before Start Date"))
    
    def on_update(self):
        if self.workflow_state == "Approved":
            self.create_or_update_employee_schedules()
    
    def create_or_update_employee_schedules(self):
        if not self.employee or not self.start_date:
            frappe.throw(_("Employee and Start Date are required"))
        
        end_date = self.end_date if self.end_date else self.start_date
        
        current_date = getdate(self.start_date)
        end_date = getdate(end_date)
        
        schedules_created = []
        schedules_updated = []
        
        while current_date <= end_date:
            result = self.get_or_create_employee_schedule(current_date)
            
            if result.get("is_new"):
                schedules_created.append(result["name"])
            else:
                schedules_updated.append(result["name"])
            
            current_date = add_days(current_date, 1)
        
        if schedules_created:
            frappe.msgprint(
                _("Created {0} Employee Schedule(s): {1}").format(
                    len(schedules_created),
                    ", ".join(schedules_created)
                ),
                indicator="green"
            )
        
        if schedules_updated:
            frappe.msgprint(
                _("Updated {0} Employee Schedule(s): {1}").format(
                    len(schedules_updated),
                    ", ".join(schedules_updated)
                ),
                indicator="blue"
            )
    
    def get_or_create_employee_schedule(self, schedule_date):
        existing_schedule = frappe.db.get_value(
            "Employee Schedule",
            {
                "employee": self.employee,
                "date": schedule_date
            },
            "name"
        )
        
        if existing_schedule:
            schedule_doc = frappe.get_doc("Employee Schedule", existing_schedule)
            
            self.update_employee_schedule_fields(schedule_doc, schedule_date)
            schedule_doc.save(ignore_permissions=True)
            
            return {
                "name": existing_schedule,
                "is_new": False
            }
        else:

            schedule_doc = frappe.new_doc("Employee Schedule")
            schedule_doc.employee = self.employee
            schedule_doc.date = schedule_date
            schedule_doc.roster_type = "Basic"
            
            self.update_employee_schedule_fields(schedule_doc, schedule_date)
            
            schedule_doc.insert(ignore_permissions=True)
            
            return {
                "name": schedule_doc.name,
                "is_new": True
            }
    
    def update_employee_schedule_fields(self, schedule_doc, schedule_date):
        schedule_doc.employee_availability = "On-the-job Training"
        
        schedule_doc.operations_role = self.operations_role
        schedule_doc.shift = self.operations_shift
        schedule_doc.site = self.operations_site
        schedule_doc.project = self.project
        
        schedule_doc.reference_doctype = "On the Job Training"
        schedule_doc.reference_docname = self.name
        schedule_doc.on_the_job_training = self.name
        
        if self.start_time and self.end_time:
            schedule_doc.start_datetime = get_datetime(f"{schedule_date} {self.start_time}")
            schedule_doc.end_datetime = get_datetime(f"{schedule_date} {self.end_time}")
            
            if self.end_time < self.start_time:
                schedule_doc.end_datetime = schedule_doc.end_datetime + timedelta(days=1)