// Copyright (c) 2026, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Subcontract Staff Attendance", {
	refresh(frm) {
		if (frm.doc.workflow_state === "Approved" && !frm.doc.__islocal) {
			frm.add_custom_button(__("Generate Invoice"), function() {
				frappe.confirm(__("Are you sure you want to generate a Purchase Invoice?"), function() {
					frappe.call({
						method: "generate_invoice",
						doc: frm.doc,
						freeze: true,
						callback: function(r) {
							if (r.message) {
								frappe.msgprint({
									title: __('Success'),
									indicator: 'green',
									message: __('Purchase Invoice {0} created successfully.', [
										`<a href="/app/purchase-invoice/${r.message}">${r.message}</a>`
									])
								});
							}
						}
					});
				});
			}).addClass("btn-primary");
		}
	},

	fetch_attendance_record: function(frm) {
		if (!frm.doc.subcontractor_name || !frm.doc.from_date || !frm.doc.to_date || !frm.doc.attendance_record_based_on) {
			frappe.msgprint(__("Please select Subcontractor Name, From Date, To Date and Attendance Record Based On."));
			return;
		}

		frm.call({
			method: "fetch_subcontractor_staff",
			doc: frm.doc,
			freeze: true,
			freeze_message: __("Fetching attendance records..."),
			callback: function(r) {
				frm.refresh_field("subcontractor_staff_attendance_item");
				frappe.msgprint({title: __("Success"), indicator: "green", message: __("Attendance records fetched successfully.")});
			}
		});
	}
});
