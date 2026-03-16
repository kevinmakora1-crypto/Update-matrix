// Copyright (c) 2025, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Event Staff", {
	client_event(frm) {
		if (frm.doc.client_event) {
			frappe.db.get_value("Client Event", frm.doc.client_event,
				["start_date", "end_date", "event_start_datetime", "event_end_datetime"],
				(r) => {
					if (r) {
						if (!frm.doc.start_date) frm.set_value("start_date", r.start_date);
						if (!frm.doc.end_date) frm.set_value("end_date", r.end_date);
						if (!frm.doc.start_datetime) frm.set_value("start_datetime", r.event_start_datetime);
						if (!frm.doc.end_datetime) frm.set_value("end_datetime", r.event_end_datetime);
					}
				}
			);
		}
	},
	end_date(frm) {
		if (frm.doc.end_date && frm.doc.end_datetime) {
			let time_part = frm.doc.end_datetime.split(" ")[1];
			if (time_part) {
				let new_end_datetime = frm.doc.end_date + " " + time_part;
				frm.set_value("end_datetime", new_end_datetime);
			}
		}
	},
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
						message = __("Do you want to Replace the Existing Employee Schedule?");
					} else {
						message = __("Employee Schedule exists for {0} out of {1} days. <br>Details: {2}. <br>Do you want to Replace the Existing Employee Schedules for conflicting days?", [conflicting_dates.length, total_days, conflicting_dates.join(", ")]);
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
