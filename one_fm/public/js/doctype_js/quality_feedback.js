frappe.ui.form.on('Quality Feedback', {
	refresh: function(frm) {
		set_feedback_schedule_stage_field(frm)
	}
});

const set_feedback_schedule_stage_field = function (frm) {
    frm.set_query('custom_feedback_schedule_stage', function () {
        return {
            filters: {
                'parent': frm.doc.custom_feedback_schedule
            }
        };
    });
}