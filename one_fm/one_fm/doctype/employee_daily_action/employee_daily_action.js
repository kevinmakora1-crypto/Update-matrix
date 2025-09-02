// Copyright (c) 2025, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Daily Action", {
    onload(frm) {
        if(frm.is_new()){
            set_employee_from_the_session_user(frm);
        }

    },
    employee(frm) {
        frm.clear_table('todays_plan_and_accomplishments');
        frm.clear_table('tomorrows_plan');
        frm.refresh_fields()

        get_todos_for_user(frm);
        get_tomorrows_todos(frm);
    }
});

function set_employee_from_the_session_user(frm) {
	if(frappe.session.user != 'Administrator' && frm.is_new() && !frm.doc.amended_from){
		frappe.db.get_value('Employee', {'user_id': frappe.session.user} , 'name', function(r) {
			if(r && r.name){
				frm.set_value('employee', r.name);
			}
			else{
				frappe.show_alert({
					message: __('Not find employee record for the user <b>{0}</b>', [frappe.session.user]),
					indicator: 'yellow'
				});
			}
		});
	}
};

async function  get_todos_for_user(frm) {
    let user_email = frm.doc.employee_email || frappe.session.user
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'ToDo',
            filters: {
                allocated_to: user_email,
                date: frappe.datetime.get_today()
            },
            fields: ['reference_name', 'reference_type', 'name', 'status','description','type'],
            limit_page_length:0
        },
        callback: function(r) {
            if (r.message) {
                frm.clear_table('todays_plan_and_accomplishments');
                r.message.forEach(function(todo) {
                    let description = "";
                    if (todo.description){
                      description = todo.description.replace(/<[^>]*>/g, "").trim();
                    }
                    let row = frm.add_child('todays_plan_and_accomplishments');
                    row.todo = todo.name;
                    row.todo_type = todo.type; // Default type, can be modified based on your needs
                    row.reference = todo.reference_name;
                    row.reference_type = todo.reference_type;
                    row.planned = 0;
                    row.completed = todo.status === 'Open' ? 0 : 1;
                    row.description = description;
                });
                frm.refresh_field('todays_plan_and_accomplishments');
            }
        }
    });
}

async function get_tomorrows_todos(frm) {
    let user_email = frm.doc.employee_email || frappe.session.user
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'ToDo',
            filters: {
                allocated_to: user_email,
                date:  frappe.datetime.add_days(frappe.datetime.get_today(), 1)
            },
            fields: ['reference_name', 'reference_type', 'name', 'type', 'description'],
            limit_page_length:0
        },
        callback: function(r) {
            if (r.message) {
                frm.clear_table('tomorrows_plan');
                r.message.forEach(function(todo) {
                    let row = frm.add_child('tomorrows_plan');
                    let description = "";
                    if (todo.description){
                      description = todo.description.replace(/<[^>]*>/g, "").trim();
                    }
                    row.todo = todo.name;
                    row.todo_type = todo.type;
                    row.reference_type = todo.reference_type;
                    row.reference = todo.reference_name;
                    row.description = description;
                });
                frm.refresh_field('tomorrows_plan');
            }
        }
    });
}
