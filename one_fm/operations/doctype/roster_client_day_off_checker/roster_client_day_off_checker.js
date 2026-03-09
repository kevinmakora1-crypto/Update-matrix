// Copyright (c) 2026, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Roster Client Day Off Checker", {
	refresh(frm) {
		// Set all fields as read-only except status for supervisors
		if (!frappe.user.has_role("System Manager")) {
			frm.set_df_property("employee", "read_only", 1);
			frm.set_df_property("date", "read_only", 1);
			frm.set_df_property("monthweek", "read_only", 1);
			frm.set_df_property("assigned_client_day_off_count", "read_only", 1);
			frm.set_df_property("client_day_off_explanation", "read_only", 1);
			frm.set_df_property("repeat_count", "read_only", 1);
		}
	},
});
