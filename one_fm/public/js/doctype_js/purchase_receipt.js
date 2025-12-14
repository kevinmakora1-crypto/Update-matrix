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

/**
 * Sets specific pricing fields in the Purchase Receipt Item grid as read-only for users with warehouse or stock-related roles.
 *
 * @param {frappe.ui.Form} frm - The current Purchase Receipt form instance.
 *
 * Business Logic:
 * - Users with any of the following roles: 'Warehouse Maintainer', 'Warehouse Supervisor', 'Stock Issuer', 'Stock Manager', or 'Stock User'
 *   (excluding users who only have default roles such as 'Assignee', 'Penalty Recipient', 'Employee', or 'Employee Self Service')
 *   are restricted from editing pricing-related fields in the Purchase Receipt Item grid.
 * - The affected fields are: 'rate', 'amount', 'discount_percentage', 'discount_amount', and 'distributed_discount_amount'.
 *
 * Business Rationale:
 * - This restriction ensures that warehouse and stock staff, whose responsibilities are operational (e.g., handling goods and stock),
 *   cannot modify pricing or discount information, which should be controlled by purchasing or finance personnel.
 * - Prevents unauthorized or accidental changes to financial data by users whose roles do not require such access.
 */
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