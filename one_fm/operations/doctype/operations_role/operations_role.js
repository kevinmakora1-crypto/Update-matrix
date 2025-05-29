// Copyright (c) 2020, omar jaber and contributors
// For license information, please see license.txt

frappe.ui.form.on('Operations Role', {
	refresh: function(frm) {
		frm.set_query("sale_item", function() {
			return {
				"filters": {
					"is_stock_item": 0,
				}
			};
		});
		let roles = ['HR Manager', 'HR User', 'Project User', 'Project Manager']
		let has_role = false;
		roles.every((item, i) => {
			if(frappe.user.has_role(item)){
				has_role = true;
				return false
			}
		});
		if(has_role){
			frm.set_df_property('status', 'read_only', false);
		} else {
			frm.set_df_property('status', 'read_only', true);
		}
	},
	before_save: function(frm) {
        if (frm.doc.status === "Inactive" && !frm.__confirmed_inactive) {
            frappe.call({
                method: "one_fm.operations.doctype.operations_role.operations_role.check_existing_schedules",
                args: {
                    operations_role: frm.doc.name
                },
                callback: function(response) {
                    if (response.message && response.data_obj && response.data_obj.is_exist) {
                        frappe.confirm(
                            "The future Employee Schedules linked to the Operations Role will be deleted on confirmation. Do you want to proceed?",
                            function () {
                                frappe.call({
                                    method: "one_fm.operations.doctype.operations_role.operations_role.delete_future_schedules",
                                    args: {
                                        operations_role: frm.doc.name
                                    },
                                    callback: function() {
                                        frm.__confirmed_inactive = true;
                                        frm.save();
                                    }
                                });
                            },
                            function () {
                                frappe.validated = false;
                                frm.reload_doc();
                            }
                        );
                    }
                }
            });

            frappe.validated = false;
        }
    }
});
