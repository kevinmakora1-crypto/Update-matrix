frappe.ui.form.on('Asset', {
    available_for_use_date: function(frm) {
        var depreciation_start_date = moment(frm.doc.available_for_use_date).endOf('month').format('YYYY-MM-DD')
        $.each(frm.doc.finance_books || [], function(i, d) {
            d.depreciation_start_date = depreciation_start_date;
		});
		refresh_field("finance_books");
	},
	refresh: function(frm){
		handle_refundable_asset_fields(frm);
		if(frm.doc.docstatus == 0){
			frm.set_value("available_for_use_date",frm.doc.purchase_date);
			refresh_field("available_for_use_date");
		}
	},
	custom_is_refundable: function(frm) {
        handle_refundable_asset_fields(frm);
    },
    
    onload: function(frm) {
        handle_refundable_asset_fields(frm);
	}
	
});


frappe.ui.form.on('Depreciation Schedule', {
	make_depreciation: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (!row.journal_entry) {
			frappe.call({
				method: "one_fm.one_fm.depreciation_custom.make_depreciation",
				args: {
					"asset_name": frm.doc.name,
					"date": row.schedule_date
				},
				callback: function(r) {
					frappe.model.sync(r.message);
					frm.refresh();
				}
			})
		}
    }
});

function handle_refundable_asset_fields(frm) {
    if (frm.doc.custom_is_refundable) {
        frm.set_value('calculate_depreciation', 0);
        frm.set_df_property('calculate_depreciation', 'read_only', 1);
        
        if (frm.doc.asset_owner !== 'Customer') {
            frm.set_value('asset_owner', 'Customer');
        }
        
        frm.set_df_property('asset_owner', 'read_only', 1);
    } else {
        frm.set_df_property('calculate_depreciation', 'read_only', 0);
        frm.set_df_property('asset_owner', 'read_only', 0);
    }
}