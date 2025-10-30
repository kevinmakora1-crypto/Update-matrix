frappe.ui.form.on('Purchase Invoice', {
    validate: function(frm){
        if(frm.doc.__islocal || frm.doc.docstatus==0){
            if(frm.doc.supplier){
                set_expense_head(frm);
            }
        }     
    },
    refresh: function(frm) {
        if (frm.doc.docstatus === 1 && frm.doc.is_refundable) {
            frm.add_custom_button(__('Sales Invoice'), function() {
                create_sales_invoice_from_purchase_invoice(frm);
            }, __('Create'));
        }
    }
});

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

function create_sales_invoice_from_purchase_invoice(frm) {
    frappe.model.open_mapped_doc({
        method: "your_app.your_module.doctype.purchase_invoice.purchase_invoice.make_sales_invoice",
        frm: frm
    });
}