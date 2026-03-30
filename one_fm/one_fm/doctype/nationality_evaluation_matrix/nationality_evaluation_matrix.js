frappe.ui.form.on('Nationality Evaluation Matrix', {
	template: function(frm) {
		if (frm.doc.template) {
			frappe.db.get_doc('Interview Evaluation Template', frm.doc.template)
				.then(template_doc => {
					frm.clear_table('weights');
					template_doc.questions.forEach(q => {
						let row = frm.add_child('weights');
						row.question = q.question;
						row.category = q.category;
						row.weight = 0; // Default weight to be filled by user
					});
					frm.refresh_field('weights');
				});
		}
	}
});
