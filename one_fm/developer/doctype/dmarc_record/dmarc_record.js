frappe.ui.form.make_control({
	df: {
		label: "DMARC Record",
		fieldtype: "Data"
	},
	parent: $("body")
});

frappe.ui.form.on("DMARC Record", {
	refresh(frm) {

	},
});
