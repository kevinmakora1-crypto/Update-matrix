import frappe
from frappe.utils import get_url, today, flt
from erpnext.quality_management.doctype.quality_feedback.quality_feedback import QualityFeedback
from one_fm.one_fm.doctype.magic_link.magic_link import create_magic_link, get_encrypted_magic_link

class QualityFeedbackOverride(QualityFeedback):
    """
    Custom override for Frappe Quality Feedback DocType.
    """
    def on_update(self):
        # Call parent's on_update if it exists
        # QualityFeedback from ERPNext may not have on_update method
        try:
            super().on_update()
        except AttributeError:
            # Parent class doesn't have on_update, skip it
            pass

        quality_score_percentage = self.calculate_quality_score_percentage()
        current_score = getattr(self, "custom_quality_score_percentage", None) or 0
        if abs(flt(current_score) - flt(quality_score_percentage)) > 0.01:  # Only update if difference > 0.01
            self.db_set("custom_quality_score_percentage", quality_score_percentage)

    def calculate_quality_score_percentage(self):
        """
        Calculate the quality score percentage.
        """
        if not self.parameters:
            return 0.0

        quality_score_percentage = 0.0
        valid_parameters = 0

        # For each parameter fetch "Rating Scale Item" count associated with "custom_rating_scale_name" 
        # and sum up "rating_score" of each "Rating Scale Item" and then find percent by formula 
        # (parameter.custom_rating_score / total_rating_score) * 100
        for parameter in self.parameters:
            if not parameter.custom_rating_scale_name:
                continue

            # Get rating scale items with rating_score field
            rating_scale_items = frappe.get_all(
                "Rating Scale Item",
                filters={"parent": parameter.custom_rating_scale_name},
                fields=["rating_score"]
            )

            if not rating_scale_items:
                continue

            total_rating_score = sum([flt(item.get("rating_score") or 0) for item in rating_scale_items])

            if total_rating_score == 0:
                continue

            parameter_rating_score = flt(parameter.custom_rating_score or 0)
            parameter_percentage = (parameter_rating_score / total_rating_score) * 100
            quality_score_percentage += parameter_percentage
            valid_parameters += 1

        if valid_parameters == 0:
            return 0.0

        return flt(quality_score_percentage / valid_parameters, precision=2)

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

@frappe.whitelist()
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
        employee_id = frappe.db.get_value("Employee", quality_feedback_doc.custom_employee, "employee_id")

        send_push_notification(employee_id, "Quality Feedback", "Please submit your quality feedback", {
            "url": magic_link_url
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