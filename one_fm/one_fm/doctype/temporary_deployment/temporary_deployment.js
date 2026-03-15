// Copyright (c) 2026, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Temporary Deployment", {
    refresh(frm) {
        // Prevent creation of Temporary Post from the Connections badge (+) button
        frm.sidebar.linked_with && frm.sidebar.linked_with.wrapper
            && frm.sidebar.linked_with.wrapper
                .find('[data-doctype="Temporary Post"] .btn-new')
                .hide();
    },

    onload_post_render(frm) {
        // Also hide after the connections panel fully renders
        setTimeout(() => {
            frm.sidebar.linked_with && frm.sidebar.linked_with.wrapper
                && frm.sidebar.linked_with.wrapper
                    .find('[data-doctype="Temporary Post"] .btn-new')
                    .hide();
        }, 500);
    }
});
