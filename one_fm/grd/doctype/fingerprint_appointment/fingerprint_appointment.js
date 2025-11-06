// Copyright (c) 2021, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fingerprint Appointment', {
    refresh: function(frm) {
        set_field_visibility_and_requirements(frm);
    },
    employee: function(frm){
        set_employee_details(frm);
        set_employee_supervisor(frm);
        
    },
    pickup_location: function(frm) {
        set_field_visibility_and_requirements(frm);
    },
	
    preparing_documents: function(frm){
        set_preparing_documents_time(frm);
    },
    before_workflow_action: function(frm) {
        try {
            let action = frm.selected_workflow_action;
            
            if (action === "Request Pickup from Accommodation") {
                frm.set_value('pickup_location', 'Accommodation');
            }
            
            if (action === "Request Pickup from Operations Site") {
                frm.set_value('pickup_location', 'Operations Site');
            }
            
            if (action === "Reject") {
                return new Promise((resolve, reject) => {
                    show_rejection_dialog(frm, resolve, reject);
                });
            }
        } catch (e) {
            console.error('Error in before_workflow_action:', e);
        }
    },
    validate: function(frm) {
        if (frm.doc.workflow_state === "Pending Supervisor" && 
            frm.doc.required_transportation === "Yes" && 
            !frm.is_new()) {
            
            let action = frm.selected_workflow_action;
            
            if (action === "Request Pickup from Accommodation") {
                if (!frm.doc.accommodation) {
                    frappe.msgprint({
                        title: __('Validation Error'),
                        message: __('Please select an Accommodation before proceeding'),
                        indicator: 'red'
                    });
                    frappe.validated = false;
                    return false;
                }
                
                if (!frm.doc.roster_action) {
                    frappe.msgprint({
                        title: __('Validation Error'),
                        message: __('Please select Roster Action before proceeding'),
                        indicator: 'red'
                    });
                    frappe.validated = false;
                    return false;
                }
            }
            
            if (action === "Request Pickup from Operations Site") {
                if (!frm.doc.operations_site) {
                    frappe.msgprint({
                        title: __('Validation Error'),
                        message: __('Please select an Operations Site before proceeding'),
                        indicator: 'red'
                    });
                    frappe.validated = false;
                    return false;
                }
            }
        }
}
});

function clear_all_overlays() {
    $('.modal-backdrop').remove();
    $('.modal').removeClass('show').hide();
    $('body').removeClass('modal-open');
    $('.modal-open').removeClass('modal-open');
    $('.freeze').remove();
    $('.overlay').remove();
    
    $('body').css({
        'padding-right': '',
        'overflow': '',
        'position': '',
        'margin-right': ''
    });
    
    $('.workflow-overlay').remove();
    $('.frappe-overlay').remove();
}

var set_employee_details = function(frm){
    if(frm.doc.employee){
        frappe.call({
            method:"frappe.client.get_value",//api calls
            args: {
                doctype:"Employee",
                filters: {
                name: frm.doc.employee
                },
                fieldname:["employee_name","one_fm_duration_of_work_permit","employee_name","one_fm_nationality","one_fm_civil_id","gender","date_of_birth","work_permit_salary","pam_file_number","employee_id","valid_upto"]
            }, 
            callback: function(r) { 
        
                // set the returned value in a field
                frm.set_value('civil_id', r.message.one_fm_civil_id);
                frm.set_value('full_name', r.message.employee_name);
				frm.set_value('first_name_arabic', r.message.one_fm_first_name_in_arabic);
                frm.set_value('second_name_arabic', r.message.one_fm_second_name_in_arabic);
                frm.set_value('third_name_arabic', r.message.one_fm_third_name_in_arabic);
                frm.set_value('last_name_arabic', r.message.one_fm_last_name_in_arabic);
                frm.set_value('employee_id',r.message.employee_id);
                frm.set_value('first_name_english', r.message.first_name);
                frm.set_value('second_name_english', r.message.middle_name);
                frm.set_value('third_name_english', r.message.one_fm_third_name);
                frm.set_value('last_name_english', r.message.last_name);
                frm.set_value('nationality', r.message.one_fm_nationality);
            }
        })
    }
};

var set_employee_supervisor = function(frm){
    if(frm.doc.employee){
        frappe.call({
            method: 'one_fm.utils.get_approver_user',
            args: {
                employee: frm.doc.employee
            },
            callback: function(r) {
                console.log(r.message);
                if (r.message) {
                    frm.set_value('employee_supervisor', r.message);
                } else {
                    frm.set_value('employee_supervisor', '');
                }
            }
        });
    } else {
        frm.set_value('employee_supervisor', '');
    }
};

var set_preparing_documents_time= function(frm){
    if(frm.doc.preparing_documents == "Yes" && !frm.doc.preparing_documents_on){
        frm.set_value('preparing_documents_on',frappe.datetime.now_datetime());
    }
}

function show_rejection_dialog(frm, resolve, reject) {
    try {
        clear_all_overlays();
        
        frappe.call({
            method: 'one_fm.grd.doctype.fingerprint_appointment.fingerprint_appointment.get_rejection_reason_options',
            callback: function(r) {
                let rejection_options = '';
                
                if (r.message) {
                    rejection_options = r.message;
                } else {
                    frappe.msgprint({
                        title: __('Configuration Error'),
                        message: __('Rejection reason options not found. Please contact administrator.'),
                        indicator: 'red'
                    });
                    reject();
                    return;
                }
                
                let dialog = new frappe.ui.Dialog({
                    title: __('Rejection Reason'),
                    fields: [
                        {
                            fieldname: 'rejection_reason',
                            label: __('Reason for Rejection'),
                            fieldtype: 'Select',
                            options: rejection_options,
                            reqd: 1
                        }
                    ],
                    primary_action_label: __('Confirm Rejection'),
                    primary_action: function(values) {
                        if (!values.rejection_reason || values.rejection_reason.trim() === '') {
                            frappe.msgprint({
                                title: __('Validation Error'),
                                message: __('Rejection reason is required'),
                                indicator: 'red'
                            });
                            return;
                        }
                        
                        frm.set_value('reason_for_rejection', values.rejection_reason);
                        
                        dialog.hide();
                        resolve();
                    },
                    secondary_action_label: __('Cancel'),
                    secondary_action: function() {
                        dialog.hide();
                        reject();
                    }
                });
                
                dialog.show();
            },
            error: function(err) {
                console.error('Error fetching rejection options:', err);
                frappe.msgprint({
                    title: __('Error'),
                    message: __('Could not load rejection options. Please try again.'),
                    indicator: 'red'
                });
                reject(err);
            }
        });
    } catch (e) {
        console.error('Error in show_rejection_dialog:', e);
        clear_all_overlays();
        reject(e);
    }
}

function set_field_visibility_and_requirements(frm) {
    if (frm.doc.workflow_state === "Pending Supervisor" && 
        frm.doc.required_transportation === "Yes" && 
        !frm.is_new()) {
        
        frm.set_df_property('pickup_location', 'hidden', 0);
        frm.set_df_property('pickup_location', 'reqd', 1);
        frm.set_df_property('roster_action', 'reqd', 1);
        frm.set_df_property('roster_action', 'hidden', 0);
        
        
        if (frm.doc.pickup_location === "Accommodation") {
            frm.set_df_property('accommodation', 'hidden', 0);
            frm.set_df_property('accommodation', 'reqd', 1);
            frm.set_df_property('operations_site', 'hidden', 1);
            frm.set_df_property('operations_site', 'reqd', 0);
        } else if (frm.doc.pickup_location === "Operations Site") {
            frm.set_df_property('operations_site', 'hidden', 0);
            frm.set_df_property('operations_site', 'reqd', 1);
            frm.set_df_property('accommodation', 'hidden', 1);
            frm.set_df_property('accommodation', 'reqd', 0);
        } else {
            frm.set_df_property('accommodation', 'hidden', 1);
            frm.set_df_property('accommodation', 'reqd', 0);
            frm.set_df_property('operations_site', 'hidden', 1);
            frm.set_df_property('operations_site', 'reqd', 0);
        }
    }
}