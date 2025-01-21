// Copyright (c) 2022, omar jaber and contributors
// For license information, please see license.txt

frappe.ui.form.on('ONEFM General Setting', {
	refresh: function(frm) {
		if(!frm.is_new()){
			frm.trigger('setup_face_recognition');
			frm.trigger('sync_google_tasks_with_erp_todos');
		}
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
	sync_google_tasks_with_erp_todos(frm){
		frm.add_custom_button('Sync Google Tasks', ()=>{
			frappe.call({
				method: 'one_fm.overrides.todo.sync_google_tasks_with_todos'
			}).then(res=>{
				frappe.msgprint(res.message.message)
			})
		}, 'Actions')
		
	},
});
