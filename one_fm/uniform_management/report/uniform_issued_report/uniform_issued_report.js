// Copyright (c) 2016, ONE FM and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Uniform Issued Report"] = {
	"filters": [
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname":"returned_on",
			"label": __("Return Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.now_date()
		}
	]
};
