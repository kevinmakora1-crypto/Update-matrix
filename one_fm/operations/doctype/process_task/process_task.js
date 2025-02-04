// Copyright (c) 2023, omar jaber and contributors
// For license information, please see license.txt

frappe.ui.form.on('Process Task', {
	refresh: function(frm) {
		set_filters(frm);
		set_custom_buttons(frm);
	},
	is_erp_task: function(frm) {
		// Prevent infinite loop
		if (frm.ignore_is_erp_task) {
			frm.ignore_is_erp_task = false;
			return;
		}

		let current_value = frm.doc.is_erp_task;
		let previous_value = !current_value; // Get the opposite value

		frappe.confirm(
			__('Are you sure you want to {0} ERP Task?', [current_value ? 'enable' : 'disable']),
			function() {
				// User clicked "Yes", do nothing (keep the change)
			},
			function() {
				// User clicked "No", revert the change without triggering the event
				frm.ignore_is_erp_task = true; // Set flag to avoid recursion
				frm.set_value('is_erp_task', previous_value);
			}
		);
	}
});

var set_custom_buttons = function(frm) {
	set_task_and_auto_repeat(frm);
	remove_task_and_auto_repeat(frm);
};

var remove_task_and_auto_repeat = function(frm) {
	if (frm.doc.task_reference || frm.doc.auto_repeat_reference){
		frm.add_custom_button(__("Remove Task and Auto Repeat"), function() {
			if(frm.is_dirty()){
				frappe.throw(__('Please Save the Document and Continue .!'))
			}
			else{
				frappe.call({
					method: "remove_task_and_auto_repeat",
					doc: frm.doc,
					callback: function(r){
						if(!r.exc){
							frm.reload_doc()
						}
					},
					freeze: true,
					freeze_message: __('Remove Task and Auto Repeat')
				});
			}
		});
	}
};

var set_task_and_auto_repeat = function(frm) {
	if (!frm.doc.task_reference && !frm.doc.auto_repeat_reference && !frm.doc.is_erp_task){
		frm.add_custom_button(__("Set Task and Auto Repeat"), function() {
			if(frm.is_dirty()){
				frappe.throw(__('Please Save the Document and Continue .!'))
			}
			else{
				frappe.call({
					method: "set_task_and_auto_repeat",
					doc: frm.doc,
					callback: function(r){
						if(!r.exc){
							frm.reload_doc()
						}
					},
					freeze: true,
					freeze_message: __('Setting up Task and Auto Repeat')
				});
			}
		});
	}
};

var set_filters = function(frm) {

	frm.set_query("task_type", function() {
		return {
			filters: {'is_routine_task': true}
		}
	});
};
