// Copyright (c) 2022, ONE FM and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Roster Projection View"] = {
	"filters": [
        {
            "fieldname":"date",
            "label": __("Date"),
            "fieldtype": "Date"
        }
	]
};
