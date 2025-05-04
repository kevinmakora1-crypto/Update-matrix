frappe.ui.form.on('Employees Not Rostered', {
    take_action(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row.employee) {
            frappe.msgprint("Employee not selected.");
            return;
        }

        frappe.db.get_doc('Employee', row.employee).then(employee => {
            const url = `/app/roster?main_view=roster&sub_view=basic&roster_type=basic&employee_id=${employee.employee_id}&shift=${row.shift_allocation}`;
            window.open(url, '_blank');
        });
    }
});
