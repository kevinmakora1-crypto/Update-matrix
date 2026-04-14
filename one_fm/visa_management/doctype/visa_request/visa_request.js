// Copyright (c) 2026, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Visa Request", {
	before_workflow_action: async function(frm) {
		try {
			let action = frm.selected_workflow_action;

			if (action === "Reject") {
				try {
					const state = frm.doc.workflow_state;

					const handledStates = [
						'Pending Initial Review',
						'Pending GRD Manager Approval',
						'Pending By PAM',
						'Pending By MOI'
					];

					if (handledStates.includes(state)) {
						return new Promise((resolve, reject) => {
							show_rejection_dialog(frm, resolve, reject);
						});
					}
				} catch (e) {
					console.error('Error handling Reject before_workflow_action:', e);
				}
			}
		} catch (e) {
			console.error('Error in before_workflow_action (visa_request):', e);
		}
	}
});


function show_rejection_dialog(frm, resolve, reject) {
	frappe.dom.unfreeze();
	frappe.prompt(
		[
			{
				label: 'Reason for Rejection',
				fieldname: 'reason',
				fieldtype: 'Small Text',
				reqd: 1
			}
		],
		function(values) {
			try {
				if (!values.reason || values.reason.length <= 10 || values.reason.trim() === "" || values.reason.trim().length < 3) {
					frappe.msgprint({
						title: __('Too Short'),
						message: __('Please ensure to provide a description of the reason'),
						indicator: 'red'
					});
					return;
				}

				const state = frm.doc.workflow_state;
				let target_field = null;

				if (state === 'Pending Initial Review') {
					target_field = 'operator_rejection_remark';
				} else if (state === 'Pending GRD Manager Approval') {
					target_field = 'grd_manager_remark';
				} else if (state === 'Pending By PAM') {
					target_field = 'pam_rejection_remark';
				} else if (state === 'Pending By MOI') {
					target_field = 'moi_rejection_remark';
				}

				if (!target_field) {
					target_field = 'rejection_remarks';
				}

				frappe.dom.freeze();
				frm.set_value(target_field, values.reason);
				try {
					if (frm.fields_dict && frm.fields_dict[target_field]) {
						frm.refresh_field(target_field);
					}
				} catch (e) {
					// ignore refresh errors
				}

				frm.save()
					.then(() => resolve())
					.catch(err => reject(err));
			} catch (err) {
				frappe.dom.unfreeze();
				reject(err);
			}
		},
		'Enter Rejection Remark',
		'Proceed'
	);
}

