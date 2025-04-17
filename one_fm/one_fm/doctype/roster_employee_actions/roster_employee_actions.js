// Copyright (c) 2021, omar jaber and contributors
// For license information, please see license.txt

frappe.ui.form.on('Roster Employee Actions', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on('Employees Not Rostered', {
    take_action(frm, cdt, cdn) {
        const row = locals[cdt][cdn];

        const employee = row.employee;
		const employee_name = row.employee_name;
        const missing_dates = row.date;
		const shift_allocation = row.shift_allocation;
        const url = `/app/roster?employee=${employee}&employee_name=${employee_name}&missing_dates=${missing_dates}&shift_allocation=${shift_allocation}`;
        window.location.href = url;
    }
});
