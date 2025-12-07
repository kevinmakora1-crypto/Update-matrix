// Copyright (c) 2025, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Event Staff", {
	before_submit(frm) {
		if (frm.doc.user_confirmed_replace) {
			return;
		}

		frappe.call({
			method: "one_fm.one_fm.doctype.event_staff.event_staff.get_conflicting_dates",
			args: {
				employee: frm.doc.employee,
				start_date: frm.doc.start_date,
				end_date: frm.doc.end_date,
			},
			callback: function (r) {
				if (r.message && r.message.length > 0) {
					let conflicting_dates = r.message;
					let total_days = frappe.datetime.get_day_diff(frm.doc.end_date, frm.doc.start_date) + 1;
					let message = "";

					if (conflicting_dates.length === total_days) {
						message = __("Warning: Do you want to Replace the Existing Employee Schedule?");
					} else {
						message = __("Warning: Employee Schedule exists for {0} out of {1} days. <br>Details: {2}. <br>Do you want to Replace the Existing Employee Schedules for conflicting days?", [conflicting_dates.length, total_days, conflicting_dates.join(", ")]);
					}

					frappe.confirm(
						message,
						() => {
							// User clicked Yes
							frm.doc.user_confirmed_replace = 1;
							frm.save("Submit");
						},
						() => {
							// User clicked No
							frappe.validated = false;
							frappe.msgprint(__("Submission Cancelled"));
						}
					);
					// Pause the submission until the user responds
					frappe.validated = false;
				}
			},
			freeze: true,
			freeze_message: __("Checking for schedule conflicts...")
		});
	},
});
