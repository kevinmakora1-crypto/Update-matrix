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
    status(frm) {
        if (frm.doc.status == "Pending Review") {
            // Set completed_by from the first person in the 'assign_to' field
            if (frm.doc.custom_assigned_to) {
                frm.set_value("completed_by", frm.doc.custom_assigned_to[0]["user"]);
            }

            // Set completed_on as today's date
            frm.set_value("completed_on", frappe.datetime.get_today());
        }
    },
    refresh: function (frm) {
        set_perms(frm);  
        }
})

function set_perms(frm){
    let {project} = frm.doc;
    frappe.xcall('one_fm.overrides.task.get_roles_and_validate_is_manager', {project})
    .then(res => {
        if(!res.exc){
            let roles = res[0];
            let is_project_manager = res[1];
            // if project is linked and session user is project manager, then Projects Manager perms apply otherwise Projects User perms apply.
            // if there is no project, then only the doc.owner can change the task status and priority.
            if (roles.includes("Projects User") && !roles.includes("Projects Manager") && !is_project_manager && (project || (frm.doc.owner != frappe.session.user))){
                // If task status is one of ["Open", "Working", "Pending Review"], keep the status field editable.
                // If task status is one of ["Overdue", "Template", "Completed", "Canceled"], make the status field read_only for Projects User.
                if(USER_PERMS["status"].includes(frm.doc.status)){
                    frm.set_df_property("status", "options", USER_PERMS["status"]);
                } else {
                    frm.set_df_property("status", "read_only", 1);
                }
                frm.set_df_property("priority", "read_only", USER_PERMS["priority"]);
                frm.set_df_property("completed_by", "read_only", USER_PERMS["completed_by"]);
                frm.set_df_property("completed_on", "read_only", USER_PERMS["completed_on"]);
                frm.set_df_property("exp_start_date", "read_only", USER_PERMS["exp_start_date"]);
                frm.set_df_property("exp_end_date", "read_only", USER_PERMS["exp_end_date"]);                
            } 
        }
    })
}


