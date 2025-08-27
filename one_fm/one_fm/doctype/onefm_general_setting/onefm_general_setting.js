// Copyright (c) 2022, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on('ONEFM General Setting', {
	refresh: function(frm) {
		if(!frm.is_new()){
			frm.trigger('setup_face_recognition');
		}
		frm.fields_dict['sync_google_tasks_btn'].df.hidden = !frm.doc.google_task_synchronization_enabled;
        frm.refresh_field('sync_google_tasks_btn');
	},
	setup_face_recognition(frm){
		frm.add_custom_button('Setup Face Recognition', ()=>{
			frappe.call({
				method: 'one_fm.api.utils.set_up_face_recognition_server_credentials'
			}).then(res=>{
				frappe.msgprint(res.message.message)
			})
		}, 'Actions')
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
