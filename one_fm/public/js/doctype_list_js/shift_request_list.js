frappe.listview_settings['Shift Request'] = {
    onload: function(listview) {
        if (!frappe.user_roles.includes('System Manager')) {
            setTimeout(() => {
                const actions_menu = listview.page.actions_btn_group;
                if (actions_menu) {
                    actions_menu.find('.dropdown-item').each(function() {
                        const text = $(this).text().trim();
                        if (['Approve', 'Reject', 'Return To Draft'].includes(text)) {
                            $(this).remove();
                        }
                    });
                }
            }, 200);

            listview.$result.on('change', '.list-check-all, .list-row-check', function() {
                setTimeout(() => {
                    const actions_menu = listview.page.actions_btn_group;
                    if (actions_menu) {
                        actions_menu.find('.dropdown-item').each(function() {
                            const text = $(this).text().trim();
                            if (['Approve', 'Reject', 'Return To Draft'].includes(text)) {
                                $(this).remove();
                            }
                        });
                    }
                }, 200);
            });
        }
    }
};