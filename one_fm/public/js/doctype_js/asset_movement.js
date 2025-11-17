frappe.ui.form.on('Asset Movement', {
    onload: function(frm) {
        if (frappe.route_options) {
            frm.set_value('rfm_reference', frappe.route_options.rfm_reference);
            frm.set_value('purpose', frappe.route_options.purpose);
            frm.set_df_property('purpose', 'read_only', 1);

            frappe.route_options.asset_items.forEach(item => {
                for (let i = 0; i < item.custom_pending_quantity; i++) {
                    let row = frm.add_child('items');
                    row.item_code = item.item_code;
                    row.source_warehouse = item.warehouse;
                    row.target_warehouse = item.t_warehouse;
                    row.rfm_item_reference = item.name;
                }
            });
            frm.refresh_field('items');
            frappe.route_options = null;
        }
    },

    before_workflow_action:function(frm){
        if(frm.doc.delivery_receipt == undefined && frm.doc.workflow_state == 'Pending'){
            frappe.throw("Please attatch signed copy of delivery receipt.");
        }
    }
});

frappe.ui.form.on('Asset Movement Item', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let asset_field = frm.get_field('items').grid.grid_rows_by_docname[cdn].grid_form.fields.asset;

        asset_field.get_query = function() {
            return {
                filters: {
                    'item_code': row.item_code,
                    'status': 'Active'
                }
            };
        };
    }
});
