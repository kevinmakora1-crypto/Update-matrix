frappe.ui.form.on('Roster Employee Actions', {
    refresh(frm) {
        frm.add_custom_button(__('Take Action'), function() {
            console.log(frm.doc)
            const url = `/app/roster?main_view=roster&sub_view=basic&roster_type=basic&employee_id=${frm.doc.employee_id}&shift=${frm.doc.shift}`;
            window.open(url, '_blank');
        });
    }
});
