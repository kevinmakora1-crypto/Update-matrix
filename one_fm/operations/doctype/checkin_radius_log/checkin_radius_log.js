// Copyright (c) 2022, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Checkin Radius Log', {
	refresh: function(frm) {
        frm.disable_save();
	}
});