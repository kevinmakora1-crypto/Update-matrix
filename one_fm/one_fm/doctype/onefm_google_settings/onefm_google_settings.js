// Copyright (c) 2025, omar jaber and contributors
// For license information, please see license.txt

frappe.ui.form.on("ONEFM Google Settings", {
	refresh: function (frm) {
        frm.fields_dict['sync_google_tasks_btn'].df.hidden = !frm.doc.google_task_synchronization_enabled;
        frm.refresh_field('sync_google_tasks_btn');
    },
    sync_google_tasks_btn: function (frm) {
        if(frm.doc.google_task_synchronization_enabled) {
            frappe.call({
                method: 'one_fm.overrides.todo.sync_google_tasks_with_todos'
            }).then(res => {
                frappe.msgprint(res.message.message)
            })
        }
    }
});
