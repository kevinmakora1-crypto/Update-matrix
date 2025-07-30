// Copyright (c) 2025, omar jaber and contributors
// For license information, please see license.txt

const status_color_map = {
	"P": "green",
	"WFH": "green",
	"A": "red",
	"OL": "red",
	"H": "blue",
	"DO": "blue",
	"CDO": "blue"
};

frappe.query_reports["Operations Monthly Attendance Sheet"] = {
	"filters": [
		{
			fieldname: "month",
			label: __("Month"),
			fieldtype: "Select",
			reqd: 1,
			options: [
				{ value: 1, label: __("Jan") },
				{ value: 2, label: __("Feb") },
				{ value: 3, label: __("Mar") },
				{ value: 4, label: __("Apr") },
				{ value: 5, label: __("May") },
				{ value: 6, label: __("June") },
				{ value: 7, label: __("July") },
				{ value: 8, label: __("Aug") },
				{ value: 9, label: __("Sep") },
				{ value: 10, label: __("Oct") },
				{ value: 11, label: __("Nov") },
				{ value: 12, label: __("Dec") },
			],
			default: frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth() + 1,
			on_change: function (report) {
				attach_report_additional_day_details().then(() => {
					report.refresh();
				})
			}
		},
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Select",
			reqd: 1,
			on_change: function (report) {
				attach_report_additional_day_details().then(() => {
					report.refresh();
				})
			}
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
			reqd: 1
		},
		{
			fieldname: "site",
			label: __("Site"),
			fieldtype: "Link",
			options: "Operations Site",
			depends_on: "eval: doc.project",
			get_query: function () {
				const project = frappe.query_report.get_filter_value("project");
				return {
					filters: {
						project: project || ""
					}
				};
			}
		},
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		return column.colIndex < 3 ? value : `<span style='color:${status_color_map[value]}'>${value}</span>`;
	},
	onload: function (report) {
		return frappe.call({
			method: "one_fm.one_fm.report.operations_monthly_attendance_sheet.operations_monthly_attendance_sheet.get_attendance_years",
			callback: function (r) {
				const year_filter = report.get_filter("year")
				year_filter.df.options = r.message;
				year_filter.df.default = r.message.split("\n")[0];
				year_filter.refresh();
				year_filter.set_input(year_filter.df.default);
				attach_report_additional_day_details()
			},
		});
	}
};

function attach_report_additional_day_details () {
	const report = frappe.query_report;

	const selectedMonth = report.get_filter("month").value
	const selectedYear = report.get_filter("year").value

	return frappe.call({
		method: "one_fm.one_fm.report.operations_monthly_attendance_sheet.operations_monthly_attendance_sheet.get_report_additional_day_details",
		args: {
			month: selectedMonth,
			year: selectedYear
		},
		callback: function (res) {
			frappe.query_report.additional_details = {
				...(report.additional_details || {}),
				days: res.message
			};
		},
	});
}
