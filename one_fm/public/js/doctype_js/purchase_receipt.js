frappe.ui.form.on('Purchase Receipt', {
    onload: function(frm) {
        set_readonly_for_warehouse_users(frm);
    },
    
    refresh: function(frm) {
        set_readonly_for_warehouse_users(frm);
    }
});

frappe.ui.form.on('Purchase Receipt Item', {
    items_add: function(frm, cdt, cdn) {
        set_readonly_for_warehouse_users(frm);
    }
});

function set_readonly_for_warehouse_users(frm) {
    const warehouse_roles = [
        'Warehouse Maintainer',
        'Warehouse Supervisor',
        'Stock Issuer',
        'Stock Manager',
        'Stock User'
    ];
    
    const readonly_fields = [
        'rate',
        'amount',
        'discount_percentage',
        'discount_amount',
        'distributed_discount_amount'
    ];
    
    const user_roles = frappe.user_roles;
    
    const has_only_warehouse_roles = user_roles.some(role => 
        warehouse_roles.includes(role)
    ) && !user_roles.includes('Accounts Manager') 
       && !user_roles.includes('Accounts User')
       && !user_roles.includes('Purchase Manager')
       && !user_roles.includes('Purchase User');
    
    if (has_only_warehouse_roles) {
        frm.fields_dict.items.grid.update_docfield_property(
            readonly_fields,
            'read_only',
            1
        );
        
        frm.fields_dict.items.grid.fields_map.rate.df.read_only = 1;
        frm.fields_dict.items.grid.fields_map.amount.df.read_only = 1;
        frm.fields_dict.items.grid.fields_map.discount_percentage.df.read_only = 1;
        frm.fields_dict.items.grid.fields_map.discount_amount.df.read_only = 1;
        frm.fields_dict.items.grid.fields_map.distributed_discount_amount.df.read_only = 1;
        
        frm.refresh_field('items');
    }
}