// Copyright (c) 2024, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Reliever Assignment", {
	setup (frm) {
        let today = moment().format("YYYY-MM-DD");
        frm.set_query("leave_application", () => {
            return {
                filters: {
                    workflow_state: "Approved",
                    from_date: ["<=", today],
                    to_date: [">=", today],
                    custom_reliever_ : ["is", "set"]
                }
            }
        }) 
	},
});
