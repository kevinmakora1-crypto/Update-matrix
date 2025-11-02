// Copyright (c) 2021, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fingerprint Appointment', {
    employee: function(frm){
        set_employee_details(frm);
        set_employee_supervisor(frm);
    },
	
    preparing_documents: function(frm){
        set_preparing_documents_time(frm);
    },
        before_workflow_action: function(frm) {
        try {
            if (frm.doc.workflow_state === "Pending Supervisor") {
                let action = frm.selected_workflow_action;
                
                if (action === "Accept") {
                    return new Promise((resolve, reject) => {
                        show_acceptance_dialog(frm, resolve, reject);
                    });
                }
                
                if (action === "Reject") {
                    return new Promise((resolve, reject) => {
                        show_rejection_dialog(frm, resolve, reject);
                    });
                }
            }
        } catch (e) {
            console.error('Error in before_workflow_action:', e);
            frappe.msgprint({
                title: __('Error'),
                message: __('An error occurred. Please check console for details.'),
                indicator: 'red'
            });
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

function show_acceptance_dialog(frm, resolve, reject) {
    try {
        clear_all_overlays();
        
        let dialog = new frappe.ui.Dialog({
            title: __('Acceptance Details'),
            fields: [
                {
                    fieldname: 'pickup_location',
                    label: __('Pickup Location'),
                    fieldtype: 'Select',
                    options: ['Accommodation', ],
                    reqd: 1,
                    onchange: function() {
                        let pickup_value = dialog.get_value('pickup_location');
                        dialog.fields_dict.accommodation.df.hidden = pickup_value !== 'Accommodation';
                        dialog.fields_dict.accommodation.df.reqd = pickup_value === 'Accommodation';
                        dialog.refresh();
                    }
                },
                {
                    fieldname: 'accommodation',
                    label: __('Accommodation'),
                    fieldtype: 'Link',
                    options: 'Accommodation',
                    hidden: 1,
                    reqd: 0
                },
                {
                    fieldname: 'roster_action',
                    label: __('Roster Action'),
                    fieldtype: 'Select',
                    options: ['Yes', 'No'],
                    reqd: 1
                }
            ],
            primary_action_label: __('Confirm'),
            primary_action: function(values) {
                if (values.pickup_location === 'Accommodation' && !values.accommodation) {
                    frappe.throw(__('Accommodation is required when Pickup Location is Accommodation'));
                    return;
                }
                
                frm.set_value('pickup_location', values.pickup_location);
                frm.set_value('accommodation', values.accommodation || '');
                frm.set_value('roster_action', values.roster_action);
                
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
    } catch (e) {
        console.error('Error in show_acceptance_dialog:', e);
        clear_all_overlays();
        reject(e);
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