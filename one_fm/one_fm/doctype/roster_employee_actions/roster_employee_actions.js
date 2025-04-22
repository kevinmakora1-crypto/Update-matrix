// Copyright (c) 2021, omar jaber and contributors
// For license information, please see license.txt

frappe.ui.form.on('Roster Employee Actions', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on('Employees Not Rostered', {
    
    take_action(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const employee_name = row.employee;
        frappe.db.get_doc('Employee', employee_name).then(doc => {
            const employee = doc.employee_id
            const shift_allocation = row.shift_allocation;
            const url = `/app/roster?main_view='roster'&sub_view='basic'&roster_type='basic'&employee_id=${employee}&shift=${shift_allocation}`;
            window.open(url, '_blank');
        });
		
    }
});
