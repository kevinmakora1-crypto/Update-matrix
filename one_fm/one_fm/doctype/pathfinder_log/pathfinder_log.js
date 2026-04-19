// Copyright (c) 2025, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Pathfinder Log", {
	refresh(frm) {
		// Hide Status on new documents — it always defaults to Backlog
		// and cannot be meaningfully interacted with until the doc is saved.
		frm.toggle_display("status", !frm.is_new());

		if (!frm.is_new()) {
			frm.add_custom_button(
				__("Get Open Change Requests"),
				function () {
					frappe.call({
						method:
							"one_fm.one_fm.doctype.pathfinder_log.pathfinder_log.get_open_change_requests",
						args: {
							pathfinder_log: frm.doc.name,
						},
						freeze: true,
						freeze_message: __("Fetching open change requests…"),
						callback: function () {
							frm.reload_doc();
						},
					});
				}
			);
		}
	},
});
