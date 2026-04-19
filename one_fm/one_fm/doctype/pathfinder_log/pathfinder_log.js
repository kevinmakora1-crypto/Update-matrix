// Copyright (c) 2025, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Pathfinder Log", {
	refresh(frm) {
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
		set_deployed_read_only(frm);
	},

	status(frm) {
		set_deployed_read_only(frm);
	},
});

/**
 * Lock all user-editable fields when status is "Deployed",
 * leaving only the status field editable.
 * Restores full editability for any other status.
 */
function set_deployed_read_only(frm) {
	const is_deployed = frm.doc.status === "Deployed";
	const editable_fields = ["process_name", "goal_description", "type", "change_requests"];

	editable_fields.forEach(function (fieldname) {
		frm.set_df_property(fieldname, "read_only", is_deployed ? 1 : 0);
	});

	if (is_deployed) {
		frm.set_intro(
			__("This log is Deployed. Only the Status field can be changed."),
			"blue"
		);
	} else {
		frm.set_intro("");
	}
}
