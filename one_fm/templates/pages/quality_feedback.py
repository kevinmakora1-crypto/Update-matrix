from __future__ import unicode_literals
import frappe, json
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url, getdate, today, formatdate
from one_fm.one_fm.doctype.magic_link.magic_link import authorize_magic_link as authenticate_magic_link
from one_fm.utils import set_expire_magic_link, translate_words

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
        context.docname = frappe.db.get_value('Magic Link', magic_link, 'reference_docname')

@frappe.whitelist(allow_guest=True)
def get_feedback_data(docname):
    """
    Get feedback data for rendering the form.
    Returns employee details, questions, and related information.
    """
    try:
        doc = frappe.get_doc('Quality Feedback', docname)
        
        # Get employee details
        employee_name = doc.get('custom_employee_name') or ''
        employee_id = doc.get('custom_employee') or ''
        operation_site = doc.get('custom_operations_site') or ''
        issued_on = formatdate(doc.get('custom_issued_on')) if doc.get('custom_issued_on') else ''
        feedback_schedule = doc.get('custom_feedback_schedule') or ''

        item_type = frappe.db.get_value('Quality Feedback Template', doc.template, 'custom_item_type') or ''
        
        # Get template and questions
        template = doc.get('template')
        questions = []
        
        if template:
            template_doc = frappe.get_doc('Quality Feedback Template', template)
            rating_scale = template_doc.get('custom_rating_scale') or ''
            
            # Get rating scale options
            rating_type = '1-5'  # default
            if rating_scale:
                rating_scale_doc = frappe.get_doc('Rating Scale', rating_scale)
                if hasattr(rating_scale_doc, 'rating_options'):
                    rating_options = [opt.rating_option for opt in rating_scale_doc.rating_options if opt.rating_option]
                    if len(rating_options) == 10:
                        rating_type = '1-10'
                    elif any('satisfaction' in opt.lower() or 'excellent' in opt.lower() for opt in rating_options):
                        rating_type = 'satisfaction'
            
            # Get parameters (questions) from template
            if hasattr(template_doc, 'parameters'):
                for param in template_doc.parameters:
                    question_text = param.get('parameter') or ''
                    if question_text:
                        questions.append({
                            'question': question_text,
                            'rating_type': rating_type
                        })
        
        return {
            'employee_name': employee_name,
            'employee_id': employee_id,
            'operation_site': operation_site,
            'issued_on': issued_on,
            'current_feedback_schedule': feedback_schedule,
            'item_type': item_type,
            'questions': questions
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Quality Feedback Data Fetch Failed')
        return None

@frappe.whitelist(allow_guest=True)
def submit_feedback(docname, ratings=None, noticed_damage=None, damage_description=None, feedback_text=None):
    """
    Submit feedback for a given Quality Feedback document.
    Accepts ratings array, damage information, and feedback text.
    """
    try:
        doc = frappe.get_doc('Quality Feedback', docname)
        
        # Parse ratings if provided as string
        if isinstance(ratings, str):
            ratings = json.loads(ratings)
        
        # Save ratings to parameters
        if ratings and hasattr(doc, 'parameters'):
            for rating_data in ratings:
                question_index = rating_data.get('question_index', 0)
                rating_value = rating_data.get('rating')
                
                if rating_value and question_index < len(doc.parameters):
                    # Update the rating for this parameter
                    param = doc.parameters[question_index]
                    param.rating = rating_value
                    # Try to set custom rating option if field exists
                    if hasattr(param, 'custom_rating_option'):
                        param.custom_rating_option = rating_value
        
        # Save damage information
        if noticed_damage:
            if hasattr(doc, 'custom_noticed_damage'):
                doc.custom_noticed_damage = noticed_damage
        
        if damage_description:
            if hasattr(doc, 'custom_damage_description'):
                doc.custom_damage_description = damage_description
        
        # Save feedback text
        if feedback_text:
            doc.feedback = feedback_text
            # Also save to custom field if exists for backward compatibility
            if hasattr(doc, 'one_fm_unauthorized_feedback'):
                doc.one_fm_unauthorized_feedback = feedback_text
        
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        return {'success': True, 'message': _('Feedback submitted successfully.')}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Quality Feedback Submission Failed')
        return {'success': False, 'message': _('An error occurred while submitting feedback.')}

@frappe.whitelist(allow_guest=True)
def translate_text(text, target_language='en'):
    """
    Translate text using Google Translate.
    """
    try:
        if not text or target_language == 'en':
            return text
        
        translated = translate_words(text, target_language)
        return translated
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Translation Failed')
        return text  # Return original text if translation fails

@frappe.whitelist(allow_guest=True)
def get_all_languages():
    """
    Get all languages from Language doctype.
    """
    try:
        languages = frappe.get_all(
            'Language',
            fields=['name', 'language_name'],
            order_by='language_name'
        )
        return languages
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Failed to fetch languages')
        return []

@frappe.whitelist(allow_guest=True)
def translate_multiple(texts, target_language='en'):
    """
    Translate multiple texts at once.
    """
    try:
        if not texts or target_language == 'en':
            return texts if isinstance(texts, list) else [texts]
        
        if isinstance(texts, str):
            texts = json.loads(texts)
        
        translated = []
        for text in texts:
            if text:
                translated.append(translate_words(text, target_language))
            else:
                translated.append(text)
        
        return translated
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Batch Translation Failed')
        return texts if isinstance(texts, list) else [texts]
