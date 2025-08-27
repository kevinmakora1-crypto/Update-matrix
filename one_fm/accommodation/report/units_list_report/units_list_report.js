// Copyright (c) 2016, ONE FM and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Units List Report"] = {
	"filters": [
		{
			"fieldname":"accommodation",
			"label": __("Accommodation"),
			"fieldtype": "Link",
			"options": "Accommodation"
		},
		{
			"fieldname":"gender",
			"label": __("Gender"),
			"fieldtype": "Link",
			"options": "Gender"
		},
		{
			"fieldname":"bed_space_type",
			"label": __("Bed Space Type"),
			"fieldtype": "Link",
			"options": "Bed Space Type"
		},
	]
};
