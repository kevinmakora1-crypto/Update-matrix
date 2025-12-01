from __future__ import unicode_literals
import frappe, json
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url, getdate, today
from one_fm.one_fm.doctype.magic_link.magic_link import authorize_magic_link as authenticate_magic_link
from one_fm.utils import set_expire_magic_link

def get_context(context):
    """
    Get the context for the quality feedback page.
    """
    context.title = _("Quality Feedback")

    provided_magic_link = frappe.form_dict.get('magic_link')
    
    if not provided_magic_link:
        frappe.throw(_("Magic Link is required to access this page."))

    # Authenicate Magic Link
    magic_link = authenticate_magic_link(provided_magic_link, 'Quality Feedback', 'Quality Feedback')
    if magic_link:
        context.quality_feedback = frappe.get_doc('Quality Feedback', frappe.db.get_value('Magic Link', magic_link, 'reference_docname'))

@frappe.whitelist(allow_guest=True)
def submit_feedback(docname, feedback):
    """
    Submit feedback for a given Quality Feedback document.
    """
    try:
        doc = frappe.get_doc('Quality Feedback', docname)
        # Using a custom field to store the feedback from unauthorized users
        doc.set('one_fm_unauthorized_feedback', feedback)
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return 'success'
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Quality Feedback Submission Failed')
        return 'error'
