// Copyright (c) 2021, omar jaber and contributors
// For license information, please see license.txt
frappe.ui.form.on('Roster Employee Actions', {
	onload(frm) {
		render_buttons_in_child(frm);
	}
});

function render_buttons_in_child(frm) {
    (frm.doc.employees_not_rostered || []).forEach((row, i) => {
        const button_html = `<button class="btn btn-xs btn-primary" onclick="takeAction('${row.name}')">Take Action</button>`;
        frappe.model.set_value(row.doctype, row.name, 'take_action', button_html);
    });
}
window.takeAction = function(rowname) {
    const row = frappe.get_doc(cur_frm.doc.doctype, cur_frm.doc.name)
        .employees_not_rostered.find(r => r.name === rowname);

    if (!row || !row.employee) {
        frappe.msgprint("No employee data found.");
        return;
    }

    frappe.db.get_doc('Employee', row.employee).then(employee => {
        const url = `/app/roster?main_view=roster&sub_view=basic&roster_type=basic&employee_id=${employee.employee_id}&shift=${row.shift_allocation}`;
        window.open(url, '_blank');
    });
}
