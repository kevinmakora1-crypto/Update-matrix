// Copyright (c) 2026, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Formal Hearing", {
	refresh(frm) {
		toggle_create_options(frm);
	},
	under_company_accommodation(frm) {
		toggle_create_options(frm);
	},
	reason_for_absence(frm) {
		toggle_create_options(frm);
	},
	hr_managers_decision(frm) {
		toggle_create_options(frm);
	},
	general_managers_decision(frm) {
		toggle_create_options(frm);
	},
	did_not_attend_first_hearing(frm) {
		toggle_create_options(frm);
	},
	did_not_attend_rescheduled_hearing(frm) {
		toggle_create_options(frm);
	}
});

function toggle_create_options(frm) {
	// Initially remove all custom buttons from "Create" group to avoid duplicates
	frm.remove_custom_button(__("Leave Extension"), __("Create"));
	frm.remove_custom_button(__("Unpaid Leave"), __("Create"));
	frm.remove_custom_button(__("Resignation By Law"), __("Create"));
	frm.remove_custom_button(__("Site Transfer"), __("Create"));

	if (frm.doc.docstatus !== 1) return;

	const is_found = frm.doc.under_company_accommodation == 1;
	const reason = frm.doc.reason_for_absence;
	const hr_decision = frm.doc.hr_managers_decision;
	const gm_decision = frm.doc.general_managers_decision;

	let show_leave = false;
	let show_resignation = false;
	let show_transfer = false;

	// Case 1: Found + To Pressurize
	if (is_found && reason === "To Pressurize the Company") {
		if (gm_decision === "Terminate") {
			show_resignation = true;
		}
		if (hr_decision === "Do not Terminate" || gm_decision === "Do not Terminate") {
			show_leave = true;
		}
	}

	// Case 2: Found + Work Issue
	// Phase 2: Show only when Workflow State is "Submitted"
	if (is_found && reason === "Work Issue" && frm.doc.workflow_state === "Submitted") {
		show_leave = true;
		show_transfer = true;
	}

	// Legacy Case: If they missed the hearing (keeping it as a fallback if needed, but user request is specific)
	// I'll stick TO the user's specific requirements to avoid cluttering the UI.
	// If the user wants to keep the old logic too, I should merge them.
	// However, the user said "just add the option for site transfer... updated in a bit", 
	// which sounds like a refactor to match the exact requirement.

	if (show_leave) {
		add_leave_extension_button(frm);
		add_unpaid_leave_button(frm);
	}
	if (show_resignation) {
		add_resignation_button(frm);
	}
	if (show_transfer) {
		add_site_transfer_button(frm);
	}
}

function add_leave_extension_button(frm) {
	frm.add_custom_button(__("Leave Extension"), () => {
		frappe.model.with_doctype("Leave Application", () => {
			frappe.call({
				method: "one_fm.one_fm.doctype.formal_hearing.formal_hearing.make_leave_application",
				args: { source_name: frm.doc.name },
				callback: function(r) {
					if (r.message) {
						let doc = frappe.model.get_new_doc("Leave Application");
						$.extend(doc, r.message);
						frappe.set_route("Form", "Leave Application", doc.name);
					}
				}
			});
		});
	}, __("Create"));
}

function add_unpaid_leave_button(frm) {
	frm.add_custom_button(__("Unpaid Leave"), () => {
		frappe.model.with_doctype("Leave Application", () => {
			frappe.call({
				method: "one_fm.one_fm.doctype.formal_hearing.formal_hearing.make_leave_application",
				args: {
					source_name: frm.doc.name,
					leave_type: "Leave without Pay"
				},
				callback: function(r) {
					if (r.message) {
						let doc = frappe.model.get_new_doc("Leave Application");
						$.extend(doc, r.message);
						frappe.set_route("Form", "Leave Application", doc.name);
					}
				}
			});
		});
	}, __("Create"));
}

function add_resignation_button(frm) {
	frm.add_custom_button(__("Resignation By Law"), () => {
		frappe.model.with_doctype("Employee Resignation", () => {
			frappe.call({
				method: "one_fm.one_fm.doctype.formal_hearing.formal_hearing.make_employee_resignation",
				args: { source_name: frm.doc.name },
				callback: function(r) {
					if (r.message) {
						let doc = frappe.model.get_new_doc("Employee Resignation");
						$.extend(doc, r.message);
						frappe.set_route("Form", "Employee Resignation", doc.name);
					}
				}
			});
		});
	}, __("Create"));
}

function add_site_transfer_button(frm) {
	frm.add_custom_button(__("Site Transfer"), () => {
		frappe.set_route("Form", "Employee", frm.doc.employee).then(() => {
			setTimeout(() => {
				if (cur_frm && cur_frm.doctype === "Employee" && cur_frm.docname === frm.doc.employee) {
					cur_frm.scroll_to_field("shift_working_html");
				}
			}, 1000);
		});
	}, __("Create"));
}