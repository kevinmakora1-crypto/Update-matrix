// Copyright (c) 2026, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Resignation", {
	onload: function(frm) {
		let show_date = !frm.doc.__islocal && frm.doc.workflow_state && frm.doc.workflow_state !== "Draft";
		frm.toggle_display("relieving_date", show_date);
	},

	refresh: function (frm) {
		// Hide Relieving Date for Employees (Draft phase), show once assigned to Supervisor
		let show_date = !frm.doc.__islocal && frm.doc.workflow_state && frm.doc.workflow_state !== "Draft";
		frm.toggle_display("relieving_date", show_date);

		if (!frm.doc.__islocal && frm.doc.docstatus < 2) {
			// Check if any withdrawal already exists
			frappe.db.count("Employee Resignation Withdrawal", {
				filters: {
					employee_resignation: frm.doc.name,
					docstatus: ["<", 2]
				}
			}).then(count => {
				if (count === 0) {
					frm.add_custom_button(__("Resignation Withdrawal"), function () {
						frappe.new_doc("Employee Resignation Withdrawal", {
							employee_resignation: frm.doc.name
						});
					}, __("Actions"));
				}
			});
		}
	},
	
	validate: function(frm) {
	    // Robust UI validator catch to ensure user knows EXACTLY what is blocking the save if it's the frontend!
	    if (!frm.doc.employees || frm.doc.employees.length === 0) {
	        frappe.msgprint({
	            title: __('Missing Information'),
	            message: __('You must add at least one Resigning Employee before saving.'),
	            indicator: 'red'
	        });
	        frappe.validated = false;
			return;
	    }

		// Prevent Workflow transition natively, stopping the save and elegantly preventing screen freezes.
		if (frm.selected_workflow_action === "Submit to Supervisor") {
			for (let row of frm.doc.employees) {
				if (!row.resignation_letter) {
					let emp_name = row.employee_name || row.employee;
					frappe.msgprint({
						title: __('Missing Attachment'),
						message: __('Missing Attachment for <b>{0}</b>. Please click the pencil edit icon ✏️ on their row and attach the resignation letter before submitting.', [emp_name]),
						indicator: 'red'
					});
					frappe.validated = false;
					return;
				}
			}
		}
	},

	before_workflow_action: function(frm) {
		if (frm.selected_workflow_action === "Submit to Supervisor") {
			if (frm.doc.employees && frm.doc.employees.length > 0) {
				for (let row of frm.doc.employees) {
					if (!row.resignation_letter) {
						let emp_name = row.employee_name || row.employee;
						
						frappe.msgprint({
							title: __('Missing Attachment'),
							message: __('Missing Attachment for <b>{0}</b>. Please click the pencil edit icon ✏️ on their row and attach the resignation letter before submitting.', [emp_name]),
							indicator: 'red'
						});

						// Absolute guarantee to unlock the Frappe UI freeze right after Promise rejection
						setTimeout(() => {
							frappe.dom.unfreeze();
						}, 100);

						return Promise.reject("Missing Attachment");
					}
				}
			}
		}
	},

	after_workflow_action: function(frm) {
		if (frm.doc.replacement_required === "Yes" && frm.doc.workflow_state === "Approved") {
			// Find the newly created PR and jump to it
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Project Manpower Request',
					filters: { employee_resignation: frm.doc.name },
					fieldname: 'name'
				},
				callback: function(r) {
					if (r.message && r.message.name) {
						frappe.set_route('Form', 'Project Manpower Request', r.message.name);
						frappe.show_alert({
							message: __('Auto-redirecting to Project Manpower Request for finalization...'),
							indicator: 'green'
						});
					}
				}
			});
		}
	},

	on_submit: function(frm) {
		if (frm.doc.replacement_required === "Yes") {
			// Find the newly created PR and jump to it
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Project Manpower Request',
					filters: { employee_resignation: frm.doc.name },
					fieldname: 'name'
				},
				callback: function(r) {
					if (r.message && r.message.name) {
						frappe.set_route('Form', 'Project Manpower Request', r.message.name);
						frappe.show_alert({
							message: __('Auto-redirecting to Project Manpower Request for finalization...'),
							indicator: 'green'
						});
					}
				}
			});
		}
	},

	employee: function (frm) {
		// Legacy field triggers inside JS, safely disabled
	}
});

frappe.ui.form.on('Employee Resignation Item', {
    employee: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (row.employee) {
            frappe.db.get_value('Employee', row.employee, ['project', 'department', 'designation', 'site', 'employment_type', 'shift', 'custom_operations_role_allocation', 'employee_name'])
                .then(r => {
                    let d = r.message;
                    if (d) {
                    	// Validation: Profile completeness check
                    	if (!d.project || !d.designation) {
                    		let missing = [];
                    		if (!d.project) missing.push("Project");
                    		if (!d.designation) missing.push("Designation");
                    		
                    		frappe.msgprint({
                    			title: 'Incomplete Employee Profile',
                    			message: `Employee <b>${d.employee_name} (${row.employee})</b> cannot be added because their profile is missing: <b>${missing.join(" and ")}</b>. Please update their Employee record first.`,
                    			indicator: 'red'
                    		});
                    		frappe.model.set_value(cdt, cdn, 'employee', '');
                    		return;
                    	}

                    	// Force the child table exactly visually immediately
                    	frappe.model.set_value(cdt, cdn, 'employee_name', d.employee_name);
                    	frappe.model.set_value(cdt, cdn, 'project_allocation', d.project);
                    	frappe.model.set_value(cdt, cdn, 'designation', d.designation);
                    	frappe.model.set_value(cdt, cdn, 'employment_type', d.employment_type);
                        // Natively sync properties if it's the first or master needs syncing
                        if (!frm.doc.project_allocation) frm.set_value('project_allocation', d.project);
                        if (!frm.doc.department) frm.set_value('department', d.department);
                        if (!frm.doc.designation) frm.set_value('designation', d.designation);
                        if (!frm.doc.site_allocation) frm.set_value('site_allocation', d.site);
                        if (!frm.doc.employment_type) frm.set_value('employment_type', d.employment_type);
                        if (!frm.doc.shift_allocation) frm.set_value('shift_allocation', d.shift);
                        if (!frm.doc.operations_role_allocation) frm.set_value('operations_role_allocation', d.custom_operations_role_allocation);
                        
                        // Validate live Project AND Designation mismatch
                        let errors = [];
                        if (frm.doc.project_allocation && frm.doc.project_allocation !== d.project) {
                            errors.push(`Project (${d.project} vs ${frm.doc.project_allocation})`);
                        }
                        if (frm.doc.designation && frm.doc.designation !== d.designation) {
                            errors.push(`Designation (${d.designation} vs ${frm.doc.designation})`);
                        }
                        
                        if (errors.length > 0) {
                            frappe.msgprint({
                                title: 'Mismatch Error',
                                message: `Employee ${row.employee} does not match the collective batch! Mismatches: ${errors.join(", ")}. All resigning employees must share both exact Project AND Designation!`,
                                indicator: 'red'
                            });
                            frappe.model.set_value(cdt, cdn, 'employee', '');
                        }
                    }
                });
        }
    }
});
