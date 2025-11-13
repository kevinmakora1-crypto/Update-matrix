frappe.ui.form.on('Asset Movement', {
    onload: function(frm) {
        if (frm.doc.request_for_material) {
            frm.set_df_property('purpose', 'read_only', 1);
        }
    },
    before_workflow_action:function(frm){
        if(frm.doc.delivery_receipt == undefined && frm.doc.workflow_state == 'Pending'){
            frappe.throw("Please attatch signed copy of delivery receipt.");
        }
    }
});