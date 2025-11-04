frappe.ui.form.on('Purchase Invoice', {
    validate: function(frm){
        if(frm.doc.__islocal || frm.doc.docstatus==0){
            if(frm.doc.supplier){
                set_expense_head(frm);
            }
        }     
    },
    refresh: function(frm){
        add_create_sales_invoice_button(frm);
    }
});

function add_create_sales_invoice_button(frm) {
    if (frm.doc.docstatus === 1 && frm.doc.custom_refundable) {
        frappe.call({
            method: 'one_fm.overrides.purchase_invoice.check_purchase_invoice_has_pending_qty',
            args: {
                purchase_invoice: frm.doc.name
            },
            callback: function(r) {
                if (r.message) {
                    frm.add_custom_button(__('Sales Invoice'), function() {
                        create_sales_invoice_from_purchase(frm);
                    }, __('Create'));
                }
            }
        });
    }
}

function create_sales_invoice_from_purchase(frm) {
    frappe.call({
        method: 'one_fm.overrides.purchase_invoice.make_sales_invoice_from_purchase_invoice',
        args: {
            source_names: [frm.doc.name]
        },
        freeze: true,
        freeze_message: __('Creating Sales Invoice...'),
        callback: function(r) {
            if (r.message) {
                frappe.model.sync(r.message);
                frappe.set_route('Form', r.message.doctype, r.message.name);
                frappe.show_alert({
                    message: __('Sales Invoice {0} created successfully', [r.message.name]),
                    indicator: 'green'
                }, 5);
            }
        },
        error: function(r) {
            frappe.msgprint({
                title: __('Error'),
                indicator: 'red',
                message: r.message || __('Failed to create Sales Invoice')
            });
        }
    });
}

var set_expense_head = function(frm){
    frappe.call({
        method: 'frappe.client.get_value',
        args:{
            'doctype':'Supplier',
            'filters':{
                'name': frm.doc.supplier
            },
            'fieldname':[
                'expense_account'
            ]
        },
        callback:function(s){
            if (!s.exc) {
                $.each(frm.doc.items || [], function(i, v) {
                        frappe.model.set_value(v.doctype, v.name,"expense_account",s.message.expense_account)
                })
                frm.refresh_field("items");
            }
        }
    });
};

