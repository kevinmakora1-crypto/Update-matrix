// Copyright (c) 2025, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance Amendment", {
	refresh(frm) {
        frm.events.set_year_and_month(frm);
        frm.events.filter_site_by_project(frm);
        toggle_day_value_fields_in_attendance_details(frm);
    },
    fetch_attendance_record(frm){
        frappe.call({
            method: "fetch_attendance_record",
            doc: frm.doc,
            callback: function(r) {
                frm.refresh_fields();
            },
            freeze: true,
            freeze_message: "Fetching Attendance Records..."
        });
    },
    set_year_and_month(frm){
        if(frm.is_new()){
            var month_map = {
                1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 
                9: "September", 10: "October", 11: "November", 12: "December"
            }
            frm.set_value("year", frappe.datetime.get_today().substr(0,4));
            frm.set_value("month", month_map[frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth() + 1]);
        }
    },
    project(frm) {
        frm.events.filter_site_by_project(frm);
        frm.set_value("attendance_details", []);
        frm.set_value("overtime_details", []);
        frm.set_value("site", "");
    },
    year(frm){
        frm.set_value("attendance_details", []);
        frm.set_value("overtime_details", []);
    },
    month(frm){
        frm.set_value("attendance_details", []);
        frm.set_value("overtime_details", []);
    },
    site(frm){
        frm.set_value("attendance_details", []);
        frm.set_value("overtime_details", []);
    },
    attendance_based_on(frm){
        frm.set_value("attendance_details", []);
        frm.set_value("overtime_details", []);
        toggle_day_value_fields_in_attendance_details(frm);
    },
    filter_site_by_project(frm){
        // Filter Site field by selected Project
        if(frm.doc.project){
            frm.set_query("site", function() {
                return {
                    filters: {
                        project: frm.doc.project || undefined
                    }
                };
            });
        }
    }
});

function toggle_day_value_fields_in_attendance_details(frm){
    if (frm.doc.attendance_based_on === "Shift Hours") {
        frappe.meta.get_docfield("Attendance Amendment Item", "attendance_hours_section", frm.doc.name).hidden = false
        frappe.meta.get_docfield("Attendance Amendment Item", "attendance_status_section", frm.doc.name).hidden = true
    } else {
        frappe.meta.get_docfield("Attendance Amendment Item", "attendance_hours_section", frm.doc.name).hidden = true
        frappe.meta.get_docfield("Attendance Amendment Item", "attendance_status_section", frm.doc.name).hidden = false
    }
}