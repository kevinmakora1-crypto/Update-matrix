import frappe
from frappe.utils import get_url, today
from erpnext.quality_management.doctype.quality_feedback.quality_feedback import QualityFeedback
from one_fm.one_fm.doctype.magic_link.magic_link import create_magic_link, get_encrypted_magic_link

class QualityFeedbackOverride(QualityFeedback):
    """
    Custom override for Frappe Quality Feedback DocType.
    """
    def before_submit(self):
        # Call the original before_submit logic
        super(QualityFeedbackOverride, self).before_submit()
        
    @frappe.whitelist()
    def set_parameters(self):
        """
        Set the parameters for the quality feedback.
        """
        if self.template and not getattr(self, "parameters", []):
            template_parameters = frappe.get_doc("Quality Feedback Template", self.template).parameters
            
            for parameter in template_parameters:
                self.append("parameters", {
                    "parameter": parameter.parameter,
                    "custom_rating_scale_name": parameter.custom_rating_scale
                })

def get_quality_feedback_magic_link_url(quality_feedback):
    """
    Create magic link url for the quality feedback.
    """    
    # Create a magic link for the quality feedback
    magic_link = create_magic_link("Quality Feedback", quality_feedback, "Quality Feedback")

    if magic_link:
        return get_url("/quality_feedback?magic_link=") + get_encrypted_magic_link(magic_link)
    
    return None

def send_quality_feedback_magic_link_to_employee(quality_feedback):
    """
    Send a push notification to the employee to submit the quality feedback.
    """
    from one_fm.utils import send_push_notification

    magic_link_url = get_quality_feedback_magic_link_url(quality_feedback)

    # Get the quality feedback document
    quality_feedback_doc = frappe.get_doc("Quality Feedback", quality_feedback)

    if magic_link_url:
        employee_id = frappe.db.get_value("Employee", quality_feedback_doc.employee, "employee_id")

        send_push_notification(employee_id, "Quality Feedback", "Please submit your quality feedback" + quality_feedback.name, {
            "type": "open_link",
            "link": magic_link_url
        })
        return True
        
    return False

@frappe.whitelist()
def send_quality_feedback_reminders():
    """
    Sends reminders to employees to submit quality feedback.
    """
    quality_feedbacks = frappe.get_all("Quality Feedback", { "docstatus": 0, "custom_feedback_due_on": today() })

    for quality_feedback in quality_feedbacks:
        send_quality_feedback_magic_link_to_employee(quality_feedback.name)