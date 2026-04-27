// Hide Save by default; show it only when the form has unsaved changes.
// While Save is visible, the Actions menu is hidden, and vice versa.
// Applies globally to all doctypes.

function _one_fm_toggle_save_actions(frm) {
	if (!frm || !frm.page || !frm.doc) return;
	// Only interfere with Draft (docstatus 0) documents
	if (frm.doc.docstatus !== 0) return;

	const is_unsaved = frm.is_dirty() || frm.is_new();

	if (is_unsaved) {
		frm.page.btn_primary && frm.page.btn_primary.show();
		frm.page.hide_menu();
	} else {
		frm.page.btn_primary && frm.page.btn_primary.hide();
		frm.page.show_menu();
	}
}

// Run after every form refresh (covers initial load and post-save)
$(document).on('form-refresh', function (event, frm) {
	_one_fm_toggle_save_actions(frm);
});

// Intercept frm.dirty() globally so the buttons toggle the instant a form becomes dirty
const _one_fm_original_dirty = frappe.ui.form.Form.prototype.dirty;
frappe.ui.form.Form.prototype.dirty = function () {
	_one_fm_original_dirty.call(this);
	_one_fm_toggle_save_actions(this);
};
