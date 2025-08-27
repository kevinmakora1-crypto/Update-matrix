# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt
from calendar import monthrange
from itertools import groupby

import frappe
from frappe import _
from frappe.query_builder.functions import Count, Extract, Sum
from frappe.utils import cint, cstr, getdate

status_map = {
	"Role": "e.g. SG",
	"Absent": "A",
	"Day Off": "DO",
	"On Leave": "L"
}
day_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def execute(filters=None):
	filters = frappe._dict(filters or {})

	if not (filters.month and filters.year):
		frappe.throw(_("Please select month and year."))

	attendance_map = get_attendance_map(filters)
	if not attendance_map:
		frappe.msgprint(_("No attendance records found."), alert=True, indicator="orange")
		return [], [], None, None

	columns = get_columns(filters)
	data = get_data(filters, attendance_map)

	if not data:
		frappe.msgprint(_("No attendance records found for this criteria."), alert=True, indicator="orange")
		return columns, [], None, None

	message = get_message()
	
	return columns, data, message

def get_columns(filters):
	columns = []
	columns.extend([
		{
			"label": _("Employee Name"), 
			"fieldname": "employee_name", 
			"fieldtype": "Data", 
			"width": 120
		},
		{
			"label": _("Shift"), 
			"fieldname": "operations_shift", 
			"fieldtype": "Link", 
			"options": "Operations Shift",
			"width": 120
		}
	])
	columns.extend(get_columns_for_days(filters))
	return columns


def get_attendance_map(filters):
	"""Returns a dictionary of employee wise attendance map as per shifts for all the days of the month like
	{
		'employee1': {
				'Morning Shift': {1: 'Present', 2: 'Absent', ...}
				'Evening Shift': {1: 'Absent', 2: 'Present', ...}
		},
		'employee2': {
				'Afternoon Shift': {1: 'Present', 2: 'Absent', ...}
				'Night Shift': {1: 'Absent', 2: 'Absent', ...}
		},
		'employee3': {
				None: {1: 'On Leave'}
		}
	}
	"""
	attendance_list = get_attendance_records(filters)
	attendance_map = {}
	leave_map = {}
	day_off_map = {}
	for d in attendance_list:
		if d.status == "On Leave":
			leave_map.setdefault(d.employee, []).append(d.day_of_month)
			continue

		if d.status == "Day Off":
			day_off_map.setdefault(d.employee, []).append(d.day_of_month)
			continue
	
		if d.operations_shift is None:
			d.operations_shift = ""

		attendance_map.setdefault(d.employee, {}).setdefault(d.operations_shift, {})
		# For present days, add role abbreviation instead of Present
		attendance_map[d.employee][d.operations_shift][d.day_of_month] = d.post_abbrv

	# Leave days map
	for employee, leave_days in leave_map.items():
		# no attendance records exist except leaves
		if employee not in attendance_map:
			attendance_map.setdefault(employee, {}).setdefault(None, {})

		for day in leave_days:
			for shift in attendance_map[employee].keys():
				attendance_map[employee][shift][day] = "On Leave"

	# Day off map
	for employee, day_off_days in day_off_map.items():
		# no attendance records exist except leaves
		if employee not in attendance_map:
			attendance_map.setdefault(employee, {}).setdefault(None, {})

		for day in day_off_days:
			for shift in attendance_map[employee].keys():
				attendance_map[employee][shift][day] = "Day Off"


	return attendance_map

def get_attendance_records(filters):
	Attendance = frappe.qb.DocType("Attendance")
	OperationsRole = frappe.qb.DocType("Operations Role")
	query = (
		frappe.qb.from_(Attendance)
		.left_join(OperationsRole)
		.on(Attendance.operations_role == OperationsRole.name)
		.select(
			Attendance.employee,
			Extract("day", Attendance.attendance_date).as_("day_of_month"),
			Attendance.status,
			Attendance.operations_shift,
			OperationsRole.post_abbrv
		)
		.where(
			(Attendance.docstatus == 1)
			& (Attendance.company == filters.company)
			& (Attendance.site == filters.operations_site)
			& (Extract("month", Attendance.attendance_date) == filters.month)
			& (Extract("year", Attendance.attendance_date) == filters.year)
		)
	)
	if filters.project:
		query = query.where(Attendance.project == filters.project)

	if filters.roster_type:
		query = query.where(Attendance.roster_type == filters.roster_type)

	if filters.employee:
		query = query.where(Attendance.employee == filters.employee)
	query = query.orderby(Attendance.employee, Attendance.attendance_date)
	return query.run(as_dict=1)

@frappe.whitelist()
def get_attendance_years():
	"""Returns all the years for which attendance records exist"""
	Attendance = frappe.qb.DocType("Attendance")
	year_list = (
		frappe.qb.from_(Attendance).select(Extract("year", Attendance.attendance_date).as_("year")).distinct()
	).run(as_dict=True)

	if year_list:
		year_list.sort(key=lambda d: d.year, reverse=True)
	else:
		year_list = [frappe._dict({"year": getdate().year})]

	return "\n".join(cstr(entry.year) for entry in year_list)


def get_message() -> str:
	message = ""
	colors = ["green", "red", "black", "#318AD8"]

	count = 0
	for status, abbr in status_map.items():
		message += f"""
			<span style='border-left: 2px solid {colors[count]}; padding-right: 12px; padding-left: 5px; margin-right: 3px;'>
				{status} - {abbr}
			</span>
		"""
		count += 1

	return message


def get_columns_for_days(filters):
	total_days = get_total_days_in_month(filters)
	days = []

	for day in range(1, total_days + 1):
		day = cstr(day)
		# forms the dates from selected year and month from filters
		date = f"{cstr(filters.year)}-{cstr(filters.month)}-{day}"
		# gets abbr from weekday number
		weekday = day_abbr[getdate(date).weekday()]
		# sets days as 1 Mon, 2 Tue, 3 Wed
		label = f"{day} {weekday}"
		days.append({"label": label, "fieldtype": "Data", "fieldname": day, "width": 65})

	return days


def get_total_days_in_month(filters):
	return monthrange(cint(filters.year), cint(filters.month))[1]


def get_data(filters, attendance_map):
	employee_details = get_employee_related_details(filters)
	data = []

	data = get_rows(employee_details, filters, attendance_map)

	return data


def get_rows(employee_details, filters, attendance_map):
	records = []

	for employee, details in employee_details.items():

		employee_attendance = attendance_map.get(employee)
		if not employee_attendance:
			continue

		attendance_for_employee = get_attendance_status_for_detailed_view(
			employee, filters, employee_attendance
		)
		# set employee details
		for row in attendance_for_employee:
			row.update({"employee_name": details.employee_name})#"employee": employee, 

		records.extend(attendance_for_employee)

	return records

def get_attendance_status_for_detailed_view(employee, filters, employee_attendance):
	"""Returns list of shift-wise attendance status for employee
	[
			{'shift': 'Morning Shift', 1: 'A', 2: 'P', 3: 'A'....},
			{'shift': 'Evening Shift', 1: 'P', 2: 'A', 3: 'P'....}
	]
	"""
	total_days = get_total_days_in_month(filters)
	attendance_values = []
	for shift, status_dict in employee_attendance.items():
		row = {"operations_shift": shift}

		for day in range(1, total_days + 1):
			status = status_dict.get(day)
			abbr = status_map.get(status, "") if status in ["Absent", "On Leave", "Day Off"] else status
			row[cstr(day)] = abbr

		attendance_values.append(row)

	return attendance_values

def get_employee_related_details(filters):
	"""Returns
	1. nested dict for employee details
	"""
	Employee = frappe.qb.DocType("Employee")
	query = (
		frappe.qb.from_(Employee)
		.select(
			Employee.name,
			Employee.employee_name,
			Employee.designation,
			Employee.grade,
			Employee.department,
			Employee.branch,
			Employee.company,
			Employee.holiday_list,
		)
		.where(Employee.company == filters.company)
	)

	if filters.employee:
		query = query.where(Employee.name == filters.employee)


	employee_details = query.run(as_dict=True)

	emp_map = {}

	for emp in employee_details:
		emp_map[emp.name] = emp

	return emp_map