# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt

from datetime import timedelta

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, add_days, get_datetime



class OntheJobTraining(Document):
    def validate(self):
        self.validate_dates()
        self.validate_extension_request()
        self.calculate_total_scheduled_ojt_days()

    def validate_extension_request(self):
        if self.is_extension_request and self.original_ojt_request:
            original_ojt = frappe.get_doc("On the Job Training", self.original_ojt_request)
            if not original_ojt.end_date:
                frappe.throw(_("Original OJT Request must have an End Date."))

            if getdate(self.start_date) <= getdate(original_ojt.end_date):
                frappe.throw(_("Extension Start Date must be after the End Date of the Original OJT Request."))

    def calculate_total_scheduled_ojt_days(self):
        if self.start_date and self.end_date:
            days = (getdate(self.end_date) - getdate(self.start_date)).days + 1
            if self.is_extension_request and self.original_ojt_request:
                original_ojt_days = frappe.db.get_value("On the Job Training", self.original_ojt_request, "total_scheduled_ojt_days")
                self.total_scheduled_ojt_days = original_ojt_days + days
            else:
                self.total_scheduled_ojt_days = days

    def validate_dates(self):
        today = getdate(frappe.utils.nowdate())

        if self.start_date and getdate(self.start_date) < today:
            frappe.throw(_("The scheduled event Start date can not be a past date."))

        if self.end_date and getdate(self.end_date) < today:
            frappe.throw(_("The scheduled event End date can not be a past date."))

        if self.start_date and self.end_date:
            if getdate(self.end_date) < getdate(self.start_date):
                frappe.throw(
                    _("The scheduled end date must be later than Start Date. Please adjust the event details.")
                )
    
    def on_update(self):
        if self.workflow_state == "Approved":
            if self.has_value_changed("end_date"):
                self.handle_end_date_change()
            else:
                self.create_or_update_employee_schedules()
    
    def create_or_update_employee_schedules(self):
        if not self.employee or not self.start_date:
            frappe.throw(_("Employee and Start Date are required"))

        end_date = self.end_date if self.end_date else self.start_date
        self.create_schedules_in_range(self.start_date, end_date)
    
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

    def handle_end_date_change(self):
        old_doc = self.get_doc_before_save()
        today = getdate(frappe.utils.nowdate())
        end_date = getdate(self.end_date)
        old_end_date = getdate(old_doc.end_date) if old_doc.end_date else today

        if end_date < today:
            frappe.throw(_("Past dates cannot be provided in End Date field."))

        if end_date == today:
            checkin_exists = frappe.db.exists(
                "Employee Checkin",
                {
                    "employee": self.employee,
                    "date": today,
                },
            )
            if checkin_exists:
                frappe.throw(
                    _("Cannot update the record for {0}").format(self.employee)
                )
            else:
                self.delete_schedules_from_date(today)
                return

        if end_date < old_end_date:
            self.delete_schedules_from_date(add_days(end_date, 1))
        elif end_date > old_end_date:
            start_creation_date = add_days(old_end_date, 1)
            self.create_schedules_in_range(start_creation_date, end_date)

    def create_schedules_in_range(self, start_date, end_date):
        current_date = getdate(start_date)
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
                    len(schedules_created), ", ".join(schedules_created)
                ),
                indicator="green",
            )
        if schedules_updated:
            frappe.msgprint(
                _("Updated {0} Employee Schedule(s): {1}").format(
                    len(schedules_updated), ", ".join(schedules_updated)
                ),
                indicator="blue",
            )

    def delete_schedules_from_date(self, start_date):
        schedules_to_delete = frappe.get_all(
            "Employee Schedule",
            filters={
                "employee": self.employee,
                "on_the_job_training": self.name,
                "date": [">=", start_date],
            },
            pluck="name",
        )
        if schedules_to_delete:
            for doc in schedules_to_delete:
                frappe.delete_doc("Employee Schedule", doc, ignore_permissions=True)
            frappe.msgprint(
                _("Deleted {0} Employee Schedule(s)").format(len(schedules_to_delete)),
                indicator="red",
            )
@frappe.whitelist()
def create_ojt_extension(source_name, target_doc=None):
	source_doc = frappe.get_doc("On the Job Training", source_name)

	doc = frappe.new_doc("On the Job Training")

	doc.is_extension_request = 1
	doc.original_ojt_request = source_doc.name

	doc.on_the_job_training_name = source_doc.on_the_job_training_name
	doc.employee = source_doc.employee
	doc.employee_name = source_doc.employee_name
	doc.employee_id = source_doc.employee_id
	doc.operations_role = source_doc.operations_role
	doc.operations_shift = source_doc.operations_shift
	doc.operations_site = source_doc.operations_site
	doc.operations_supervisor = source_doc.operations_supervisor
	doc.project = source_doc.project
	doc.operations_manager = source_doc.operations_manager
	doc.mentor = source_doc.mentor
	doc.mentor_name = source_doc.mentor_name
	doc.client_agreed_ojt_days = source_doc.client_agreed_ojt_days

	return doc