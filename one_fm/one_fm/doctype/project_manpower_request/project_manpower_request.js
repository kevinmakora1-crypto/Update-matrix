// Copyright (c) 2026, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project Manpower Request', {
	refresh: function(frm) {
		// Set ERF filter: only active ERFs matching this designation
		frm.set_query('erf', function() {
			return {
				filters: {
					designation: frm.doc.designation,
					docstatus: 1,
					status: ['not in', ['Cancelled', 'Closed']]
				}
			};
		});
	},

	designation: function(frm) {
		// Clear ERF when designation changes since the filter context changes
		frm.set_value('erf', '');
	},

	before_submit: function(frm) {
		if (!frm.doc.erf) {
			frappe.validated = false;

			// Check if any active ERF exists for this designation
			frappe.call({
				method: 'frappe.client.get_count',
				args: {
					doctype: 'ERF',
					filters: {
						designation: frm.doc.designation,
						docstatus: 1,
						status: ['not in', ['Cancelled', 'Closed']]
					}
				},
				async: false,
				callback: function(r) {
					if (r.message === 0) {
						frappe.msgprint({
							title: __('No ERF Found'),
							message: __('Please create an ERF for designation <b>{0}</b> before submitting this Project Manpower Request.', [frm.doc.designation]),
							indicator: 'red'
						});
					} else {
						frappe.msgprint({
							title: __('ERF Required'),
							message: __('Please select an ERF before submitting this Project Manpower Request.'),
							indicator: 'orange'
						});
					}
				}
			});
		}
	}
});
