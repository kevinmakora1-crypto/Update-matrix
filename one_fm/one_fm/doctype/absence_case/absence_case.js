// Copyright (c) 2026, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Absence Case", {
	refresh(frm) {
		frm.set_query("leave_application", function() {
			return {
				filters: {
					"leave_type": "Annual Leave"
				}
			};
		});

		if (frm.doc.docstatus === 1 && frm.doc.received_leave_extension_request === "Yes" && frm.doc.leave_application) {
			frm.add_custom_button(__("Leave Extension Request"), function() {
				frappe.new_doc("Leave Extension Request", {
					"employee": frm.doc.employee,
					"leave_application": frm.doc.leave_application
				});
			}, __("Create"));
		}
	},
});
