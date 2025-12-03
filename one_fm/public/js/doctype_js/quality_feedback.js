frappe.ui.form.on('Quality Feedback', {
	refresh: function(frm) {
		set_feedback_schedule_stage_field(frm)
        add_copy_magic_link_button(frm)
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

const add_copy_magic_link_button = function (frm) {
    frm.add_custom_button(__('Copy Magic Link'), function () {
       frappe.call({
        method: 'one_fm.overrides.quality_feedback.get_quality_feedback_magic_link_url',
        args: {
            quality_feedback: frm.doc.name
        },
        callback: function (r) {
            if (r.message) {
                navigator.clipboard.writeText(r.message);
                frappe.show_alert({
                    message: __('Magic link copied to clipboard'),
                    indicator: 'green'
                });
            }
        }
       });
    });
}