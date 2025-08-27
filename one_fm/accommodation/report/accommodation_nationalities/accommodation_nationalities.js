// Copyright (c) 2022, ONE FM and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Accommodation Nationalities"] = {
	"filters": [
        {
            "fieldname": "accommodation",
            "label": __("Accommodation"),
            "fieldtype": "Link",
            "options": "Accommodation"
        },
	]
};
