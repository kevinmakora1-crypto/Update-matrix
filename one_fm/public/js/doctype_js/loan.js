frappe.ui.form.on('Loan', {
    refresh: function(frm) {
    if (frm.doc.docstatus == 1 && 
            frm.doc.repay_from_salary && 
            frm.doc.applicant_type == 'Employee' && 
            ['Partially Disbursed', 'Disbursed'].includes(frm.doc.status)) {
            frm.add_custom_button(__('Additional Repayment'), function() {
                show_additional_repayment_dialog(frm);
    }, __('Create'));
    }
}
});

function show_additional_repayment_dialog(frm) {
    let dialog = new frappe.ui.Dialog({
        title: __('Additional Repayment'),
        fields: [
            {
                fieldname: 'date',
                fieldtype: 'Date',
                label: __('Date'),
                reqd: 1,
                default: frappe.datetime.get_today()
            },
            {
                fieldname: 'repayment_account',
                fieldtype: 'Link',
                label: __('Repayment Account'),
                options: 'Account',
                reqd: 1,
                get_query: function() {
                    return {
                        filters: {
                            'account_type': ['in', ['Bank', 'Cash']],
                            'is_group': 0,
                            "disabled": 0,
                            'company': frm.doc.company 
                        }
                    };
                }
            },
            {
                fieldname: 'paid_amount',
                fieldtype: 'Currency',
                label: __('Paid Amount'),
                reqd: 1,
                precision: 2
            }
        ],
        size: 'small', 
        primary_action_label: __('Create Repayment'),
        primary_action: function(values) {

            if (!values.date || !values.repayment_account || !values.paid_amount) {
                frappe.msgprint(__('Please fill all required fields'));
                return;
            }
            
            frappe.show_alert({
                message: __('Creating additional repayment...'),
                indicator: 'blue'
            });
            
            frappe.call({
                method: 'one_fm.overrides.loan.create_additional_repayment',
                args: {
                    'parent_doc': frm.doc.name,
                    'date': values.date,
                    'repayment_account': values.repayment_account,
                    'paid_amount': values.paid_amount
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __('Additional repayment created successfully'),
                            indicator: 'green'
                        });
                        frm.refresh();
                        dialog.hide();
                    } else {
                        frappe.msgprint(__('Error creating additional repayment'));
                    }
                },
                error: function(r) {
                    frappe.msgprint(__('Error: ') + r.message);
                }
            });
        },
        secondary_action_label: __('Cancel')
    });
    
    dialog.show();
}