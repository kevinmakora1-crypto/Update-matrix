// Copyright (c) 2025, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Pathfinder Log", {
	refresh(frm) {
		// Restrict Epic link field to Work Items of type "Epic" only
		frm.set_query("epic", function () {
			return {
				filters: {
					work_item_type: "Epic",
				},
			};
		});

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
