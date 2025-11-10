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
				method: "one_fm.utils.get_approver_user",
				args : {"employee": frm.doc.employee},
				callback: function (r) {
					if(r && r.message){
						frm.set_value("employee_supervisor", r.message);
					}
				}
			});
		}
	},
	before_workflow_action: async function(frm){
		let workflow_states = ["Set Pick-up as Accommodation (Supervisor)", "Pending Supervisor"];
		if (frm.selected_workflow_action == "Reject" && workflow_states.includes(frm.doc.workflow_state) && !frm.doc.reason_for_rejection) {
			await new Promise((resolve, reject) => {
                frappe.dom.unfreeze();
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
			});
		}
	}
});
