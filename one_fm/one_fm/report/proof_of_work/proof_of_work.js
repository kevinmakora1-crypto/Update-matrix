// Copyright (c) 2025, ONE FM and contributors
// For license information, please see license.txt

frappe.query_reports["Proof of Work"] = {
	"filters": [
        {
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"reqd": 1 ,
			"options": [
				{ "value": 1, "label": __("Jan") },
				{ "value": 2, "label": __("Feb") },
				{ "value": 3, "label": __("Mar") },
				{ "value": 4, "label": __("Apr") },
				{ "value": 5, "label": __("May") },
				{ "value": 6, "label": __("June") },
				{ "value": 7, "label": __("July") },
				{ "value": 8, "label": __("Aug") },
				{ "value": 9, "label": __("Sep") },
				{ "value": 10, "label": __("Oct") },
				{ "value": 11, "label": __("Nov") },
				{ "value": 12, "label": __("Dec") },
			],
			"default": frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth() + 1
		},
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Select",
			"reqd": 1
		},
		{
			"fieldname":"operations_site",
			"label": __("Operations Site"),
			"fieldtype": "Link",
			"options": "Operations Site",
			"reqd": 1
		},
		{
			"fieldname":"project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options": "Project",
			"reqd": 0
		},
		{
			"fieldname":"roster_type",
			"label": __("Roster Type"),
			"fieldtype": "Select",
			"options": "\nBasic\nOver-Time",
			"reqd": 0
		},
	],
    onload: function() {
		frappe.call({
			method: "one_fm.one_fm.report.proof_of_work.proof_of_work.get_attendance_years",
			callback: function(r) {
				var year_filter = frappe.query_report.get_filter('year');
				year_filter.df.options = r.message;
				year_filter.df.default = r.message.split("\n")[0];
				year_filter.refresh();
				year_filter.set_input(year_filter.df.default);
			}
		});
	},
    formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
        if (column.colIndex > 2){
            if (value == "A") value = "<span style='color:red'>" + value + "</span>";
            else if (value == "DO") value = "<span style='color:black'>" + value + "</span>";
            else if (value == "L") value = "<span style='color:#318AD8'>" + value + "</span>";
            else value = "<span style='color:green'>" + value + "</span>";
        }

		return value;
	},
};
