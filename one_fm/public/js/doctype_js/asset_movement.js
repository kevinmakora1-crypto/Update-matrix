frappe.ui.form.on('Asset Movement', {
    onload: function(frm) {
        frm.set_query('asset', 'assets', function(doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            return {
                filters: {
                    'item_code': row.rfm_item_code,
                    'status': ["not in", ["Draft"]]
                }
            };
        });
    },
    before_workflow_action:function(frm){
        if(frm.doc.delivery_receipt == undefined && frm.doc.workflow_state == 'Pending'){
            frappe.throw("Please attach signed copy of delivery receipt.");
        }
    }
});