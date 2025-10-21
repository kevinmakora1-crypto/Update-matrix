const USER_PERMS = {
    status: ["Open", "Working", "Pending Review"],
    priority: true,
    completed_by: false,
    completed_on: true,
    exp_start_date: false,
    exp_end_date: false,
    //due date - no such field
}

frappe.ui.form.on("Task", {
    refresh: function (frm) {
        set_perms(frm);  
        }
})

function set_perms(frm) {
    let { project } = frm.doc;
    frappe.xcall("one_fm.overrides.task.get_roles_and_validate_is_manager", { project })
        .then(res => {
            if (!res.exc) {
                let roles = res[0];
                let is_project_manager = res[1];

                // Lock entire form.
                if (!roles.includes("Projects Manager") && !roles.includes("Projects User") && !is_project_manager && frm.doc.owner !== frappe.session.user) {
                    Object.keys(frm.fields_dict || {}).forEach(f => frm.set_df_property(f, "read_only", 1));
                    return;
                }
                frm.set_df_property("priority", "read_only", USER_PERMS["priority"]);
                frm.set_df_property("completed_by", "read_only", USER_PERMS["completed_by"]);
                frm.set_df_property("completed_on", "read_only", USER_PERMS["completed_on"]);
                frm.set_df_property("exp_start_date", "read_only", USER_PERMS["exp_start_date"]);
                frm.set_df_property("exp_end_date", "read_only", USER_PERMS["exp_end_date"]);                
            } 
        }
    )
}


