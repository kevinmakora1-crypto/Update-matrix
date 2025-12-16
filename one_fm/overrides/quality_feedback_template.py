import frappe
from frappe import _
from erpnext.quality_management.doctype.quality_feedback_template.quality_feedback_template import QualityFeedbackTemplate

class QualityFeedbackTemplateOverride(QualityFeedbackTemplate):
    """
    Custom override for Frappe Quality Feedback Template DocType.
    """
    pass

@frappe.whitelist()
def get_damaged_attachments(quality_feedback_template: str) -> list:
    """
    Get the damaged attachments for the quality feedback template.
    
    Args:
        quality_feedback_template: Name of the Quality Feedback Template
        
    Returns:
        List of dictionaries containing damaged attachment details
    """
    # Validate input
    if not quality_feedback_template:
        frappe.throw(_("Quality Feedback Template is required"))
    
    # Check if template exists
    if not frappe.db.exists("Quality Feedback Template", quality_feedback_template):
        frappe.throw(_("Quality Feedback Template {0} not found").format(quality_feedback_template))
    
    # Check permission on template
    template_doc = frappe.get_doc("Quality Feedback Template", quality_feedback_template)
    template_doc.check_permission("read")
    
    # Get all Quality Feedbacks linked to this template where damage was noticed
    # custom_noticed_damage is a Select field with options "Yes"/"No", so we check for "Yes"
    quality_feedbacks = frappe.get_all(
        "Quality Feedback",
        filters={
            "template": quality_feedback_template,
            "custom_noticed_damage": "Yes"
        },
        fields=["name", "custom_damage_attachment", "creation"]
    )
    
    damaged_attachments = []
    
    for feedback in quality_feedbacks:
        # Check if damage attachment exists
        if feedback.custom_damage_attachment:
            # Get file details if it's a file URL
            file_url = feedback.custom_damage_attachment
            
            # Try to get file document details
            file_name = frappe.db.get_value(
                "File",
                {"file_url": file_url},
                "file_name"
            ) or file_url.split("/")[-1]  # Fallback to filename from URL
            
            damaged_attachments.append({
                "quality_feedback": feedback.name,
                "file_url": file_url,
                "file_name": file_name,
                "created_on": feedback.creation
            })
    
    return damaged_attachments