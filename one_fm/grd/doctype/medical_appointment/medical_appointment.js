// Copyright (c) 2025, one_fm and contributors
// For license information, please see license.txt

frappe.ui.form.on("Medical Appointment", {
	employee(frm) {
		frm.events.fetch_approver(frm);
	},
	fetch_approver(frm) {
		frm.set_value("employee_supervisor", null);
		if(frm.doc.employee){
			frappe.call({
				method: "one_fm.utils.get_employee_site_supervisor_user",
				args : {"employee": frm.doc.employee},
				callback: function (r) {
					if(r && r.message){
						frm.set_value("employee_supervisor", r.message);
					}
				}
			});
		}
	},
	before_workflow_action(frm) {
		frm.events.validate_payment_invoice(frm);
		return new Promise((resolve, reject) => {
			frappe.dom.unfreeze();
			frm.events.capture_rejection_reason(frm, resolve, reject);
		});
	},
	capture_rejection_reason(frm, resolve, reject){
		let workflow_states = ["Set Pick-up as Accommodation (Supervisor)", "Pending Supervisor"];
		if (frm.selected_workflow_action == "Reject" && workflow_states.includes(frm.doc.workflow_state) && !frm.doc.reason_for_rejection) {
			var dialog = new frappe.ui.Dialog({
				title: __("Reason for Rejection"),
				fields: [
					{
						label: __("Reason for Rejection"),
						fieldname: "reason_for_rejection",
						fieldtype: "Select",
						options: "\nStaff Shortage\nAnother Employee has appointment from same site\nClient requested another appointment",
						reqd: 1
					}
				],
				primary_action_label: __("Confirm"),
				primary_action(values) {
					frm.set_value("reason_for_rejection", values.reason_for_rejection);
					dialog.hide();
					frm.save()
						.then(resolve)
						.catch(reject);
				}
			});
			dialog.show();
		}
		else {
			resolve();
		}
	},
	validate_payment_invoice(frm) {
		if (frm.selected_workflow_action == "Employee Attended" && !frm.doc.payment_invoice) {
			frappe.dom.unfreeze();
			frm.scroll_to_field("payment_invoice");
		}
	}
});
