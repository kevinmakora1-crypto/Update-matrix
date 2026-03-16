// Copyright (c) 2026, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Resignation", {
	employee: function (frm) {
		// Trigger server-side fetch_from fields and supervisor auto-fill
		if (frm.doc.employee) {
			frm.refresh_fields();
		}
	}
});
