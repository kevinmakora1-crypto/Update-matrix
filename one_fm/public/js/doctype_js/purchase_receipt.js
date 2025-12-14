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
    const default_roles = [
        'Assignee',
        'Penalty Recipient',
        'Employee',
        'Employee Self Service'
    ];
    
    const warehouse_stock_roles = [
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
    
    const user_roles = frappe.user_roles.filter(role => 
        !default_roles.includes(role)
    );
    
    const has_warehouse_role = user_roles.some(role => 
        warehouse_stock_roles.includes(role)
    );
    
    if (has_warehouse_role) {
        readonly_fields.forEach(field => {
            frm.fields_dict.items.grid.update_docfield_property(
                field,
                'read_only',
                1
            );
        });
        
        frm.refresh_field('items');
    }
}