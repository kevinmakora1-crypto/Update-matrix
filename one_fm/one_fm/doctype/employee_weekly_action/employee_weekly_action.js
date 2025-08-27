// Copyright (c) 2025, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Weekly Action", {
    onload(frm) {
        if (frm.is_new()) {
            frm.set_value(get_week_and_year());
            fetch_employee(frm)
        }
    },
    employee(frm) {
      frm.events.load_plans_and_reports_to(frm)
    },
    load_plans_and_reports_to(frm) {
      frm.events.clear_plans_table(frm)
      if(frm.doc.employee){
        fetch_employee_reports_to(frm);
        load_todos(frm, true);
        load_todos(frm, false);
      }
    },
    clear_plans_table(frm) {
      frm.clear_table('project_progress_and_plans');
      frm.clear_table('next_week_task_plan');
      frm.refresh_fields();
    }
});

const fetch_employee = (frm) => {
    return frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name')
        .then(r => {
            if (r.message) {
                frm.set_value('employee', r.message.name);
            }
        });
};

const fetch_employee_reports_to = (frm) => {
  frappe.call({
      method: "one_fm.utils.get_approver",
      args : {"employee": frm.doc.employee},
      callback: function (r) {
          if(r && r.message){
              frm.set_value("reports_to", r.message);
          }
      }
  });
};

const get_week_and_year = () => {
    const currentDate = new Date();
    const adjustedDate = new Date(currentDate.setDate(currentDate.getDate() + 4 - (currentDate.getDay() || 7)));
    const yearStart = new Date(adjustedDate.getFullYear(), 0, 1);
    const weekNumber = Math.ceil((((adjustedDate - yearStart) / 86400000) + 1) / 7);
    return { week: weekNumber, year: adjustedDate.getFullYear() };
};

const load_todos = (frm, is_current) => {
    frappe.call({
        method: "one_fm.one_fm.doctype.employee_weekly_action.employee_weekly_action.fetch_todos",
        args: { employee:frm.doc.employee, is_current:is_current },
        callback: function (r) {
            if (r && r.status_code === 200 && Array.isArray(r.data)) {
                const fieldname = is_current ? 'project_progress_and_plans' : 'next_week_task_plan';

                r.data.forEach(item => {
                    let description = "";
                    if (item.description){
                      description = item.description.replace(/<[^>]*>/g, "").trim();
                    }
                    const row = frm.add_child(fieldname);
                    row.project = item.project;
                    row.todo = item.name;
                    row.todo_title = description;
                    if (!is_current && item.date) {
                        row.due_date = item.date;
                    }
                });

                frm.refresh_field(fieldname);
            } else {
                console.warn('No data returned from fetch_todos:', r);
            }
        }
    });
};
