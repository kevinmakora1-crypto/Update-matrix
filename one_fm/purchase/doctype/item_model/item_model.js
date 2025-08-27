// Copyright (c) 2021, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Model', {
	refresh: function(frm) {
		frm.set_query("item_group", function() {
			return {
				filters: {'is_group': 1}
			};
		});
	}
});
