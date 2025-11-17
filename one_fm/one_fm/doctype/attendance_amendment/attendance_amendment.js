// Copyright (c) 2025, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Attendance Amendment", {
	refresh(frm) {
        frm.events.set_year_and_month(frm);
        frm.events.filter_site_by_project(frm);
    },
    fetch_attendance_record(frm){
        frappe.call({
            method: "fetch_attendance_record",
            doc: frm.doc,
            callback: function(r) {
                frm.refresh_fields();
            }
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
