// Copyright (c) 2025, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leave Handover", {
	refresh(frm) {
		if (frm.doc.docstatus === 1 && frm.doc.status === "Transferred") {
			frm.add_custom_button(__("Revert"), () => {
				frappe.confirm(
					__("You are about to replace the reliever with the Leave Applicant in each of the documents referenced in the table. Do you want to proceed?"),
					() => {
						frappe.call({
							method: "one_fm.one_fm.doctype.leave_handover.leave_handover.revert_handover",
							args: {
								docname: frm.doc.name
							},
							callback: function(r) {
								if (!r.exc) {
									frm.reload_doc();
								}
							}
						});
					}
				);
			}).addClass("btn-primary");
		}
	},
	after_save(frm) {
		frm.dashboard.clear_headline();
		if (frm.doc.handover_items && frm.doc.handover_items.length > 0) {
			const doctype_counts = frm.doc.handover_items.reduce((acc, item) => {
				acc[item.reference_doctype] = (acc[item.reference_doctype] || 0) + 1;
				return acc;
			}, {});

			const message_parts = Object.entries(doctype_counts).map(([doctype, count]) => {
				return `${count} ${doctype}`;
			});

			const message = __("Found {0}. Proceed to set the relievers", [message_parts.join(", ")]);
			frm.dashboard.set_headline(message);
		}
	},
	before_submit(frm) {
		if (frm.doc.__islocal) {
			return;
		}
		frappe.confirm(
			__("You are about to replace the Employee with the Reliever in each of the documents referenced in the table. Do you want to proceed?"),
			() => {
				frm.page.btn_primary.prop('disabled', true);
				frappe.call({
					method: 'frappe.desk.form.save.submit',
					args: {
						doc: frm.doc
					},
					callback: function(r) {
						if(!r.exc) {
							frm.reload_doc();
						}
					},
					error: function(r) {
						frm.page.btn_primary.prop('disabled', false);
					}
				});
			},
			() => {
				frappe.msgprint(__("Submission cancelled."));
			}
		);
		return false; // Prevent default submission
	}
});
