// Copyright (c) 2026, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Resignation Date Adjustment", {
    onload: function(frm) {
        frm.trigger("check_corporate");
    },
    refresh: function(frm) {
        frm.trigger("check_corporate");
    },
    check_corporate: function(frm) {
        if (frm.doc.employee_resignation) {
            frappe.db.get_value('Employee Resignation', frm.doc.employee_resignation, ['project_allocation', 'site_allocation', 'department'])
            .then(r => {
                if (r && r.message) {
                    let project = r.message.project_allocation || "";
                    let site = r.message.site_allocation || "";
                    let dept = r.message.department || "";
                    let is_corporate = (project.includes("Head Office") || site.includes("Head Office") || dept.includes("Head Office"));
                    
                    // Set the dynamic property so Frappe's native Depends On engine kicks in
                    frm.doc.is_corporate = is_corporate ? 1 : 0;
                    
                    // Trigger native UI re-evaluation
                    frm.refresh_fields();
                }
            });
        }
    }
});
