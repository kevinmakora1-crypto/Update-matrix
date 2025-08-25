// Copyright (c) 2025, omar jaber and contributors
// For license information, please see license.txt


frappe.query_reports["7-Day Consecutive Absences"] = {
	"filters": [
			{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
		},
			{
			fieldname: "department",
			label: __("Department"),
			fieldtype: "Link",
			options: "Department",
		},
		{
			fieldname: "start_date",
			label: __("Start Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.add_days(frappe.datetime.get_today(), -6)
		},
		{
			fieldname: "end_date",
			label: __("End Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.get_today()
		}
	]
};