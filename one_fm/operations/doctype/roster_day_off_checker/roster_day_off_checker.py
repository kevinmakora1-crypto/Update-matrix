# Copyright (c) 2022, omar jaber and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import (
    get_first_day, get_last_day, getdate, add_days, add_months
)
from frappe.model.document import Document
from frappe.query_builder.functions import Count
from one_fm.operations.doctype.operations_shift.operations_shift import get_shift_supervisor

monthname_dict = {
	'01': 'Jan',
	'02': 'Feb',
	'03': 'Mar',
	'04': 'Apr',
	'05': 'May',
	'06': 'Jun',
	'07': 'Jul',
	'08': 'Aug',
	'09': 'Sep',
	'10': 'Oct',
	'11': 'Nov',
	'12': 'Dec',
}


class RosterDayOffChecker(Document):
	pass

def get_day_off_comparison_dates(day_off_category):
    today = getdate()
    comparison_periods = []

    if day_off_category == "Monthly":
        # Current month
        current_month_start = get_first_day(today)
        current_month_end = get_last_day(today)
        comparison_periods.append({
            "start_date": current_month_start,
            "end_date": current_month_end
        })

        # Next month
        next_month_date = add_months(today, 1)
        next_month_start = get_first_day(next_month_date)
        next_month_end = get_last_day(next_month_date)
        comparison_periods.append({
            "start_date": next_month_start,
            "end_date": next_month_end
        })

    elif day_off_category == "Weekly":
        # First 7-day period starting from tomorrow
        week1_start = add_days(today, 1)
        week1_end = add_days(week1_start, 6)
        comparison_periods.append({
            "start_date": week1_start,
            "end_date": week1_end
        })

        # Next 7-day period
        week2_start = add_days(week1_end, 1)
        week2_end = add_days(week2_start, 6)
        comparison_periods.append({
            "start_date": week2_start,
            "end_date": week2_end
        })

    return comparison_periods

def check_roster_day_off():
	# Get all active employees
	# Validate their offs for next 2 months/weeks based on their Day Off Category
	# If discrepency, create record with each employee info
	try:
		Employee = frappe.qb.DocType('Employee')
		employees = frappe.db.sql(frappe.qb.from_(Employee).select("*").where((Employee.status=="Active") & (Employee.shift_working == 1)), as_dict=1)

		today = getdate()

		for employee in employees:
			comaprison_dates = get_day_off_comparison_dates(employee.day_off_category)

			site_supervisor = frappe.db.get_value("Operations Site", employee.site, "account_supervisor")
			shift_supervisor = get_shift_supervisor(employee.shift)
			project_manager = frappe.db.get_value('Project', employee.project, 'account_manager')

			for period in comaprison_dates:	# Always 2 iterations only because we have just two period for comparison	
				day_off_data = get_employee_day_off_comparison(employee, period["start_date"], period["end_date"])

				if day_off_data["day_off_difference"]:
					duration = day_off_data["monthweek"]
		
					# Delete exising for target duration against employee
					frappe.delete_doc_if_exists("Roster Day Off Checker", f"OPR-RDOC-{employee.name}-{duration}")

					day_off_checker = frappe.new_doc("Roster Day Off Checker")
					day_off_checker.date = today
					day_off_checker.monthweek = duration
					day_off_checker.employee = employee.name
					day_off_checker.shift_supervisor = shift_supervisor
					day_off_checker.site_supervisor = site_supervisor
					day_off_checker.project_manager = project_manager
					day_off_checker.day_off_difference = day_off_data["day_off_difference"]
					day_off_checker.insert(ignore_permissions=1)

	except Exception:
		frappe.log_error(frappe.get_traceback())


def get_employee_day_off_comparison(employee, start_date, end_date):		
	EmployeeSchedule = frappe.qb.DocType("Employee Schedule")

	# QB conditions
	employee_name = (EmployeeSchedule.employee == employee.name) 
	employee_schedule_date = (EmployeeSchedule.date[start_date:end_date])
		
	# Calculate no of off days
	od = frappe.db.sql(frappe.qb.from_(EmployeeSchedule)        
		.select(Count("name").as_("off_days"))
		.where(employee_schedule_date & employee_name & (EmployeeSchedule.employee_availability == "Day Off") & (EmployeeSchedule.day_off_ot == 0))
		.groupby(EmployeeSchedule.employee), 
	as_dict=1) 
	off_days = od[0].off_days if len(od) > 0 else 0 

	# Calculate no of ot days
	ot = frappe.db.sql( frappe.qb.from_(EmployeeSchedule)
		.select(Count("name").as_("ot_days"))
		.where(employee_schedule_date & employee_name & (EmployeeSchedule.day_off_ot == 1))
		.groupby(EmployeeSchedule.employee), as_dict=1) 
	ot_days = ot[0].ot_days if len(ot) > 0 else 0 

	day_off_diff = ''
	employee_number_of_days_off = employee.number_of_days_off

	if employee_number_of_days_off != (off_days + ot_days): # If has any discrepency
		if off_days > employee_number_of_days_off and not ot_days:
			day_off_diff = f"{off_days - employee_number_of_days_off} day(s) off scheduled more, please reduce by {off_days - employee_number_of_days_off}"
		elif off_days < employee_number_of_days_off and not ot_days:
			day_off_diff = f"{employee_number_of_days_off - off_days} day(s) off scheduled less, please schedule {employee_number_of_days_off - off_days} more day off"
		elif ot_days < employee_number_of_days_off and not off_days:
			day_off_diff = f"{employee_number_of_days_off - ot_days} day(s) off OT scheduled less, please schedule {employee_number_of_days_off - ot_days} more day off"
		elif ot_days > employee_number_of_days_off and not off_days:
			day_off_diff = f"{ot_days - employee_number_of_days_off} day(s) off OT scheduled more, please schedule {ot_days - employee_number_of_days_off} day off OT less"
		elif (ot_days and off_days):
			day_off_diff = f"{ot_days} day(s) OT and {off_days} day(s) off scheduled, actual day off should be {employee_number_of_days_off}"

	start_date_split = str(start_date).split('-')
	end_date_split = str(end_date).split('-')

	return {
		"monthweek": f"{monthname_dict[start_date_split[1]]} {start_date_split[2]} - {monthname_dict[end_date_split[1]]} {end_date_split[2]}",
		"off_days": off_days,
		"ot_days": ot_days,
		"day_off_difference": day_off_diff
	}

@frappe.whitelist()
def generate_checker():
	frappe.enqueue(check_roster_day_off, queue='long', timeout=4000)