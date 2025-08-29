// Copyright (c) 2025, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Department Weekly Review", {
	onload(frm) {
        if (frm.is_new()) {
            set_current_week_and_year(frm)
            fetch_user_department(frm).then((r) => {
                frm.set_value(r.message)
                load_department_employees(frm)
                load_department_blockers(frm)
            });
        }
    },
    department: function(frm) {
        load_department_employees(frm)
        load_department_blockers(frm)
	},
});

const set_current_week_and_year = (frm) => {
    frappe.call({
        method: 'one_fm.utils.get_current_year_and_week',
        callback: function(r) {
            if (r.message) {
                frm.set_value(r.message);
            }
        }
    });
};

const fetch_user_department = () => {
    return frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'department')
};

const load_department_employees = (frm) => {
    if(!frm.doc.department) return

    frappe.call({
        method: "one_fm.one_fm.doctype.department_weekly_review.department_weekly_review.get_employees_by_department",
        args: { department: frm.doc.department },
        callback: function (r) {
            if (r.message && Array.isArray(r.message)) {
                frm.clear_table("attendees");

                r.message.forEach(emp => {
                    const row = frm.add_child("attendees");
                    row.employee = emp.name;
                    row.employee_name = emp.employee_name;
                });

                frm.refresh_field("attendees");
            }
        }
    });
};

const load_department_blockers = (frm) => {
    if(!(frm.doc.department && frm.doc.week && frm.doc.year)) return

    frappe.call({
        method: "one_fm.one_fm.doctype.department_weekly_review.department_weekly_review.get_blockers_by_department",
        args: { department: frm.doc.department, week: frm.doc.week, year: frm.doc.year },
        callback: function (r) {
            if (r.message && Array.isArray(r.message)) {
                frm.clear_table("blockers");

                r.message.forEach(item => {
                    const row = frm.add_child("blockers");
                    row.blocker = item.blocker_details;
                    row.employee_name = item.employee_name;
                    row.since = item.date;
                    row.assigned = item.assigned_to;
                });

                frm.refresh_field("blockers");
            }
        }
    });
};
