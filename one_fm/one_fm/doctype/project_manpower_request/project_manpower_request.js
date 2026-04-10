frappe.ui.form.on('Project Manpower Request', {
	refresh: function(frm) {
		setup_status_indicator(frm);
		setup_fulfillment_actions(frm);
		
		// Hide the individual backend quantity fields to keep the form clean
		frm.toggle_display([
			'cancelled_qty',
			'managed_by_ot_qty',
			'managed_by_subcontractor_qty',
			'internal_transfer_qty',
			'resignation_withdrawal_qty'
		], false);

		// Always ensure quantities visually recalculate correctly for existing documents
		let count = frm.doc.count || 0;
		let fulfilled = (frm.doc.cancelled_qty || 0) + (frm.doc.managed_by_ot_qty || 0) + 
						(frm.doc.managed_by_subcontractor_qty || 0) + (frm.doc.internal_transfer_qty || 0) + 
						(frm.doc.resignation_withdrawal_qty || 0);
		
		let expected_remaining = Math.max(0, count - fulfilled);
		if (frm.doc.remaining_qty !== expected_remaining) {
			frm.set_value('remaining_qty', expected_remaining);
		}

		let hired_count = frm.doc.fulfilled_by_employees ? frm.doc.fulfilled_by_employees.length : 0;
		let expected_to_hire = Math.max(0, expected_remaining - hired_count);
		if (frm.doc.number_to_hire !== expected_to_hire) {
			frm.set_value('number_to_hire', expected_to_hire);
		}

		// Set ERF filter
		frm.set_query('erf', function() {
			return {
				filters: {
					designation: frm.doc.designation,
					docstatus: 1,
					status: ['not in', ['Cancelled', 'Closed']]
				}
			};
		});

		// Restrict closed-by employee selection to active employees with matching designation
		frm.set_query('employee', 'fulfilled_by_employees', function() {
			return {
				filters: {
					designation: frm.doc.designation,
					status: 'Active'
				}
			};
		});
		
		// Track old status for reverting
		frm.doc.__old_status = frm.doc.status;
		
		// Enforce Exit count read-only lock
		frm.set_df_property('count', 'read_only', frm.doc.reason === 'Exit');
	},

	status: function(frm) {
		if (frm.doc.status === 'Completed') {
			let hired_count = frm.doc.fulfilled_by_employees ? frm.doc.fulfilled_by_employees.length : 0;
			let required = frm.doc.remaining_qty || 0;
			if (hired_count !== required) {
				frappe.msgprint({
					title: 'Action Blocked',
					indicator: 'red',
					message: `You cannot change the status to Completed. You must first link exactly <b>${required}</b> Employee(s) in the Closed By Employees table below.`
				});
				setTimeout(() => {
					frm.set_value('status', frm.doc.__old_status || 'In Process');
					setup_status_indicator(frm);
				}, 10);
				return;
			}
		}
		frm.doc.__old_status = frm.doc.status;
		setup_status_indicator(frm);
	},

	designation: function(frm) {
		frm.set_value('erf', '');
	},

	reason: function(frm) {
		if (frm.doc.reason === 'Exit') {
			frm.set_value('count', 1);
		}
		frm.set_df_property('count', 'read_only', frm.doc.reason === 'Exit');
	},

	before_submit: function(frm) {
		if (!frm.doc.erf) {
			frappe.validated = false;
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
	},

	validate: function(frm) {
		if (frm.doc.status === 'Completed') {
			let hired_count = frm.doc.fulfilled_by_employees ? frm.doc.fulfilled_by_employees.length : 0;
			let required = frm.doc.remaining_qty || 0;
			if (hired_count !== required) {
				frappe.msgprint({
					title: 'Missing Hired Candidates',
					indicator: 'red',
					message: `You cannot mark this PMR as Completed. You still have <b>${frm.doc.number_to_hire}</b> open slots! You must link exactly <b>${required}</b> Employee(s) in the Closed By Employees table below.`
				});
				frappe.validated = false;
			}
		}
	},

	fulfilled_by_employees_add: function(frm) {
		calculate_hired_dynamically(frm);
	},
	fulfilled_by_employees_remove: function(frm) {
		calculate_hired_dynamically(frm);
	}
});

function calculate_hired_dynamically(frm) {
	let hired_count = frm.doc.fulfilled_by_employees ? frm.doc.fulfilled_by_employees.length : 0;
	let expected_to_hire = Math.max(0, (frm.doc.remaining_qty || 0) - hired_count);
	frm.set_value('number_to_hire', expected_to_hire);
}

function setup_status_indicator(frm) {
	const status_colors = {
		"Open": "gray",
		"Pending": "gray",
		"In Process": "blue",
		"Completed": "green",
		"Cancelled": "red",
		"Internal Fulfilled": "light-green",
		"Fulfilled by OT": "blue",
		"Fulfilled by Sub-con": "purple",
		"Fulfilled by OT & Sub": "darkgray",
		"Withdrawal Resignation": "yellow"
	};
	if (frm.doc.status) {
		frm.page.set_indicator(__(frm.doc.status), status_colors[frm.doc.status] || "gray");
	}
}

function setup_fulfillment_actions(frm) {
	// Only show fulfillment actions if the document is submitted and has an active status
	if (frm.is_new() || frm.doc.docstatus === 0) return;
	
	const show_prompt = (field_name, title) => {
		let current_qty = frm.doc[field_name] || 0;
		let count = frm.doc.count || 0;
		let fulfilled_by_others = (frm.doc.cancelled_qty || 0) + 
								  (frm.doc.managed_by_ot_qty || 0) + 
								  (frm.doc.managed_by_subcontractor_qty || 0) + 
								  (frm.doc.internal_transfer_qty || 0) + 
								  (frm.doc.resignation_withdrawal_qty || 0) - current_qty;
		
		let max_allowed = count - fulfilled_by_others;

		frappe.prompt([
			{
				label: `Total ${title}`,
				fieldname: 'qty',
				fieldtype: 'Int',
				reqd: 0,
				default: current_qty,
				description: `Enter the revised total quantity. (Maximum Allowed: ${max_allowed})`
			}
		], (values) => {
			let entered_qty = values.qty || 0;
			
			if (entered_qty < 0) {
				frappe.msgprint({title: 'Invalid Qty', indicator: 'red', message: 'Quantity cannot be negative.'});
				return;
			}
			
			if (entered_qty > max_allowed) {
				frappe.msgprint({
					title: 'Exceeds Allowed', 
					indicator: 'red', 
					message: `You cannot allocate ${entered_qty}. Because of other fulfillment actions, you only have ${max_allowed} remaining out of the original count.`
				});
				return;
			}
			
			if (entered_qty === current_qty) return;

			frm.set_value(field_name, entered_qty);
			
			frm.save('Update').then(() => {
				frappe.show_alert({message: `Updated ${title} to ${entered_qty}.`, indicator: 'green'});
			});

		}, `Edit: ${title}`, 'Update');
	};

	frm.add_custom_button('Cancelled', () => show_prompt('cancelled_qty', 'Cancelled'), 'Fulfillment Action');
	frm.add_custom_button('Managed by OT', () => show_prompt('managed_by_ot_qty', 'Managed by OT'), 'Fulfillment Action');
	frm.add_custom_button('Managed by SubContractor', () => show_prompt('managed_by_subcontractor_qty', 'Managed by SubContractor'), 'Fulfillment Action');
	frm.add_custom_button('Internal Transfer', () => show_prompt('internal_transfer_qty', 'Internal Transfer'), 'Fulfillment Action');
}
