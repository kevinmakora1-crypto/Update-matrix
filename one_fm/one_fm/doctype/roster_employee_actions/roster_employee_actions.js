frappe.ui.form.on('Roster Employee Actions', {
    refresh(frm) {
        setTimeout(() => {
            // Ensure button is only added once
            frm.fields_dict["employees_not_rostered"].$wrapper
                .find('.grid-body .rows .grid-row')
                .each(function () {
                    const rowname = $(this).attr("data-name");

                    const $cell = $(this).find('[data-fieldname="take_action"]');
                    $cell.empty().append(`<button class="btn btn-xs btn-primary" data-rowname="${rowname}">Take Action</button>`);
                });

            // Off previous event bindings to prevent duplication
            frm.fields_dict["employees_not_rostered"].$wrapper
                .off('click', 'button[data-rowname]')
                .on('click', 'button[data-rowname]', function () {
                    const rowname = $(this).data("rowname");
                    const row = frm.doc.employees_not_rostered.find(r => r.name === rowname);

                    if (!row || !row.employee) {
                        frappe.msgprint("No employee data found.");
                        return;
                    }

                    frappe.db.get_doc('Employee', row.employee).then(employee => {
                        const url = `/app/roster?main_view=roster&sub_view=basic&roster_type=basic&employee_id=${employee.employee_id}&shift=${row.shift_allocation}`;
                        window.open(url, '_blank');
                    });
                });
        }, 300); // slight delay to allow table to render
    }
});
