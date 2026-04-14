// Copyright (c) 2026, ONE FM and contributors
// For license information, please see license.txt

frappe.listview_settings['Project Manpower Request'] = {
	hide_name_column: true,
	add_fields: ["workflow_state"],
	get_indicator: function (doc) {
		const status_colors = {
			"Open": "orange",
			"Pending": "gray",
			"In Process": "blue",
			"Completed": "green",
			"Cancelled": "red",
			"Internal Fulfilled": "light-green",
			"Fulfilled by OT": "blue",
			"Fulfilled by Sub-con": "purple",
			"Fulfilled by OT & Sub": "darkgray",
			"Withdrawal Resignation": "yellow"
		};
		return [__(doc.workflow_state), status_colors[doc.workflow_state] || "gray", "workflow_state,=," + doc.workflow_state];
	}
};
