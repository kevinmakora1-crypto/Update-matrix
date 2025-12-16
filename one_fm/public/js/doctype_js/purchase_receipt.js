frappe.ui.form.on('Purchase Receipt', {
    onload: function(frm) {
        setTimeout(() => {
            set_readonly_for_warehouse_users(frm);
        }, 100);
    },
    
    refresh: function(frm) {
        setTimeout(() => {
            set_readonly_for_warehouse_users(frm);
        }, 100);
    }
});

frappe.ui.form.on('Purchase Receipt Item', {
    items_add: function(frm) {
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
        'Employee Self Service',
        'All', 
        'Guest',
        'Desk User'
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
    
    // Get all roles excluding default roles
    const non_default_roles = frappe.user_roles.filter(role => 
        !default_roles.includes(role)
    );

    // Check if user has warehouse roles
    const has_warehouse_role = non_default_roles.some(role => 
        warehouse_stock_roles.includes(role)
        
    );

    
    // Get roles that are neither default nor warehouse
    const other_roles = non_default_roles.filter(role => 
        !warehouse_stock_roles.includes(role)
    );
    
    // Make read-only ONLY if user has warehouse role BUT no other roles
    if (has_warehouse_role && other_roles.length === 0) {
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




