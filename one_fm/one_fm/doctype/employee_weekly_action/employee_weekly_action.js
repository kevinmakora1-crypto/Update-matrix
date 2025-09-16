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
        load_todos(frm);
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

const load_todos = (frm) => {
    frappe.call({
        method: "one_fm.one_fm.doctype.employee_weekly_action.employee_weekly_action.fetch_todos",
        args: { employee:frm.doc.employee },
        callback: function (r) {
            if (r && r.status_code === 200 && Array.isArray(r.data)) {
                const getWeekDateRange = (offset = 0) => {
                    const now = new Date();
                    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                    const dayOfWeek = today.getDay(); // 0 for Sunday
                    const firstDay = new Date(today);
                    firstDay.setDate(today.getDate() - dayOfWeek + (offset * 7));
                    const lastDay = new Date(firstDay);
                    lastDay.setDate(firstDay.getDate() + 6);

                    const formatDate = d => d.toISOString().split('T')[0];
                    return { start: formatDate(firstDay), end: formatDate(lastDay) };
                }

                const thisWeek = getWeekDateRange(0);
                const nextWeek = getWeekDateRange(1);

                r.data.forEach(item => {
                    let description = "";
                    if (item.description){
                      description = item.description.replace(/<[^>]*>/g, "").trim();
                    }

                    if (item.date <= thisWeek.end) {
                        const row = frm.add_child('project_progress_and_plans');
                        row.project = item.project;
                        row.todo = item.name;
                        row.todo_title = description;
                    }

                    if (item.date >= nextWeek.start && item.date <= nextWeek.end) {
                        const row = frm.add_child('next_week_task_plan');
                        row.project = item.project;
                        row.todo = item.name;
                        row.todo_title = description;
                        row.due_date = item.date;
                    }
                });

                frm.refresh_field('project_progress_and_plans');
                frm.refresh_field('next_week_task_plan');
            } else {
                console.warn('No data returned from fetch_todos:', r);
            }
        }
    });
};
