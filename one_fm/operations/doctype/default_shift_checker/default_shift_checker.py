# Copyright (c) 2024, omar jaber and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count
from frappe.utils import getdate, get_last_day

class DefaultShiftChecker(Document):
    def on_submit(self):
        self.update_employee_shift_details()

    def update_employee_shift_details(self):
        """
            Updates the employee's shift or reliever status based on the action type.
        """
        employee = frappe.get_doc("Employee", self.employee)

        field_updates = {
            "Shift Allocation Update": {
                "shift": self.new_shift_allocation,
                "custom_operations_role_allocation": self.new_operations_role_allocation
            },
            "Mark Employee as Reliever": {
                "custom_is_reliever": 1
            }
        }

        if self.action_type in field_updates:
            employee.update(field_updates[self.action_type])
            employee.save()

        self.db_set("status", "Completed")


def create_default_shift_checker():
    start_date = getdate()
    last_day_of_month = get_last_day(start_date)

    threshold =  frappe.db.get_single_value("ONEFM General Setting", "default_shift_checker_threshold")

    Employee = DocType("Employee")
    EmployeeSchedule = DocType("Employee Schedule")

    query = (
        frappe.qb.from_(Employee)
        .join(EmployeeSchedule)
        .on(Employee.name == EmployeeSchedule.employee)
        .select(
            Employee.name.as_("employee"),
            Employee.shift.as_("default_shift"),
            Employee.site.as_("default_site")
        )
        .where(
            (Employee.status == "Active")
            & (Employee.shift_working == 1)
            & (Employee.custom_is_reliever != 1)
            & (Employee.shift.isnotnull())
            & (Employee.shift != EmployeeSchedule.shift)
            & (EmployeeSchedule.employee_availability == "Working")
            & (EmployeeSchedule.roster_type == "Basic")
            & (EmployeeSchedule.date[start_date:last_day_of_month])
        )
        .groupby(Employee.name)
        .having(Count(EmployeeSchedule.shift) > threshold)
    )

    result = query.run(as_dict=1)

    for item in result:
        try:
            default_shift_checker = frappe.new_doc("Default Shift Checker")
            default_shift_checker.employee = item['employee']
            default_shift_checker.start_date = start_date
            default_shift_checker.end_date = last_day_of_month
            default_shift_checker.site_supervisor = frappe.db.get_value("Operations Site", item['default_site'], "account_supervisor")

            shifts_assigned_outside = (
                frappe.qb.from_(EmployeeSchedule)
                .select(
                    EmployeeSchedule.shift,
                    Count(EmployeeSchedule.shift).as_("operations_shift_count"),
                )
                .where(
                    (EmployeeSchedule.employee == item["employee"])
                    & (EmployeeSchedule.shift != item["default_shift"])
                    & (EmployeeSchedule.employee_availability == "Working")
                    & (EmployeeSchedule.roster_type == "Basic")
                    & (EmployeeSchedule.date[start_date:last_day_of_month])
                )
                .groupby(EmployeeSchedule.shift)
            ).run(as_dict=1)

            for schedule in shifts_assigned_outside:
                default_shift_checker.append("assigned_shifts_outside_default_shift", {
                    "operations_shift": schedule.shift,
                    "count": schedule.operations_shift_count
                })
            default_shift_checker.save()
        except Exception as e:
            frappe.log_error("Default Shift Checker", frappe.get_traceback())
            continue
