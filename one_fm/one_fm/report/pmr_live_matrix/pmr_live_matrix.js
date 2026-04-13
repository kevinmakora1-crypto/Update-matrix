frappe.query_reports["PMR Live Matrix"] = {
	"add_total_row": 1,
	"filters": [
		{
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "MultiSelectList",
			"options": "\nOpen\nIn Process\nInternal Fulfilled\nFulfilled by OT\nFulfilled by Sub-con\nFulfilled by OT & Sub\nCompleted\nCancelled\nWithdrawal Resignation\nDraft",
			"get_data": function(txt) {
				let options = ["Open", "In Process", "Internal Fulfilled", "Fulfilled by OT", "Fulfilled by Sub-con", "Fulfilled by OT & Sub", "Completed", "Cancelled", "Withdrawal Resignation", "Draft"];
				return options.filter(o => o.toLowerCase().includes(txt.toLowerCase()));
			}
		},
		{
			"fieldname":"reason",
			"label": __("Manpower Type"),
			"fieldtype": "MultiSelectList",
			"options": "\nExit\nNew Project\nHigh Salary\nSubcontractor Replacement\nOvertime\nReliever",
			"get_data": function(txt) {
				let options = ["Exit", "New Project", "High Salary", "Subcontractor Replacement", "Overtime", "Reliever"];
				return options.filter(o => o.toLowerCase().includes(txt.toLowerCase()));
			}
		},
		{
			"fieldname": "project_request_code",
			"label": __("PR Code"),
			"fieldtype": "Data"
		},
		{
			"fieldname": "project_allocation",
			"label": __("Project"),
			"fieldtype": "MultiSelectList",
			"get_data": function(txt) {
				return frappe.db.get_link_options('Project', txt);
			}
		},
		{
			"fieldname": "designation",
			"label": __("Designation"),
			"fieldtype": "Data"
		},
		{
			"fieldname": "erf",
			"label": __("ERF"),
			"fieldtype": "Data"
		},
		{
			"fieldname": "nationality",
			"label": __("Nationality"),
			"fieldtype": "Data"
		},
		{
			"fieldname": "gender",
			"label": __("Gender"),
			"fieldtype": "MultiSelectList",
			"options": "\nMale\nFemale\nAny",
			"get_data": function(txt) {
				let options = ["Male", "Female", "Any"];
				return options.filter(o => o.toLowerCase().includes(txt.toLowerCase()));
			}
		}
	],
	"onload": function(report) {
		report.page.add_inner_button(__("Reset Filters"), () => {
			frappe.query_report.filters.forEach(f => {
				if (f.df.fieldtype === "MultiSelectList") {
					f.set_value([]);
				} else {
					f.set_value("");
				}
			});
			frappe.query_report.refresh();
		});

		$("<style>").prop("type", "text/css").html(`
			/* Force aggressive fluid full width container by overriding Frappe root logic */
			.container, 
			.page-container, 
			.page-head {
				max-width: 100% !important;
				width: 100% !important;
				padding-left: 5px !important;
				padding-right: 5px !important;
			}
			#page-query-report .page-content {
				max-width: 100% !important;
				padding: 0px !important;
			}
			/* Aggressively compress column padding to act like Excel */
			.frappe-control.input-max-width {
				max-width: 100% !important;
			}
			.frappe-datatable .dt-header .dt-cell--header {
				font-size: 11.5px !important;
				padding: 4px 6px !important;
				background-color: #f4f5f6 !important;
				white-space: normal !important;
				word-wrap: break-word !important;
				line-height: 1.2 !important;
			}
			.frappe-datatable .dt-cell {
				padding: 4px 6px !important;
				white-space: normal !important;
				word-wrap: break-word !important;
				line-height: 1.3 !important;
			}
			/* KPI Top Right Compact Floating Badge Styling */
			.report-summary {
				display: flex !important;
				justify-content: flex-end !important;
				border: 0 !important;
				background: transparent !important;
				padding: 0 !important;
				margin: 10px 0 5px 0 !important;
				gap: 12px !important;
			}
			.report-wrapper {
				position: relative !important;
				width: 100% !important;
			}
			.report-summary .summary-item {
				flex: none !important;
				min-width: unset !important;
				border-radius: 9999px !important;
				background-color: #eff6ff !important;
				border: 1px solid #bfdbfe !important;
				padding: 2px 10px !important;
				height: 28px !important;
				max-height: 28px !important;
				margin: 0 !important;
				display: flex !important;
				flex-direction: row !important;
				align-items: center !important;
				gap: 6px !important;
				box-shadow: none !important;
			}
			.report-summary .summary-item .summary-value {
				background-color: #3b82f6 !important;
				color: #ffffff !important;
				border-radius: 50% !important;
				padding: 0 !important;
				height: 20px !important;
				width: 20px !important;
				min-width: 20px !important;
				display: flex !important;
				align-items: center !important;
				justify-content: center !important;
				line-height: 1 !important;
				font-size: 11px !important;
				font-weight: 700 !important;
				margin: 0 !important;
				border: 0 !important;
			}
			.report-summary .summary-item .summary-label {
				font-size: 11.5px !important;
				text-transform: capitalize !important;
				color: #1e3a8a !important;
				margin: 0 !important;
				font-weight: 600 !important;
			}
		`).appendTo("head");
	}
};
