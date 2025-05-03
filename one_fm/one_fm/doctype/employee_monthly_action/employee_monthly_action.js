// Copyright (c) 2025, omar jaber and contributors
// For license information, please see license.txt
frappe.ui.form.on('Employee Monthly Action', {
    onload: function (frm) {
        if (frm.is_new()) {
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Employee',
                    filters: {
                        user_id: frappe.session.user
                    },
                    fields: ['name']
                },
                callback: function (r) {
                    if (r.message && r.message.length > 0) {
                        frm.set_value('employee', r.message[0].name);
                    }
                }
            });
            const today = new Date();
            const monthOptions = frm.fields_dict.month.df.options.split('\n');

            frm.set_value('month', monthOptions[today.getMonth()]);
            frm.set_value('year', today.getFullYear().toString());
        }
    },
        employee: function (frm) {
            console.log('Employee field changed');
          if (!frm.doc.employee) return;
      
          frappe.call({
            method: 'one_fm.overrides.goal.get_goals_for_employee',
            args: {
              employee: frm.doc.employee,
              year: frm.doc.year,
              month: frm.doc.month
            },
            callback: function (r) {
              if (r.message) {
                frm.clear_table('goal_update');
      
                r.message.forEach(goal => {
                  const row = frm.add_child('goal_update');
                  row.goal = goal.goal_name;
                  row.previous_progress = goal.progress;
                });
      
                frm.refresh_field('goal_update');
              }
            }
          });
        }
      
});
