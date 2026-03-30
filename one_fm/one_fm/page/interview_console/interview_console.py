import frappe
from frappe.utils import getdate, nowdate

def get_valid_fields():
    meta = frappe.get_meta('Job Applicant')
    return [df.fieldname for df in meta.fields]

@frappe.whitelist()
def get_applicant_data(applicant):
    """
    Returns age, remarks, score, status, and dynamic interview matrix.
    """
    valid_fields = get_valid_fields()
    res = {"age": "--", "remarks": "", "score": 0, "status": "Open", "matrix": []}
    
    # Fetch Applicant details
    applicant_doc = frappe.get_doc('Job Applicant', applicant)
    designation = applicant_doc.designation
    nationality = applicant_doc.get('one_fm_nationality')

    # Discovery for DOB (Updated with user's specific fields)
    found_dob = next((f for f in ['one_fm_date_of_birth', 'date_of_birth', 'dob', 'birth_date', 'custom_date_of_birth'] if f in valid_fields), None)
    if found_dob:
        dob = applicant_doc.get(found_dob)
        if dob:
            today = getdate(nowdate())
            birthday = getdate(dob)
            res["age"] = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
            
    # Discovery for Remarks
    found_remarks = next((f for f in ['interview_remarks', 'remarks', 'custom_remarks', 'notes'] if f in valid_fields), None)
    if found_remarks:
        res["remarks"] = applicant_doc.get(found_remarks) or ""
        
    # Discovery for Score
    found_score = next((f for f in ['interview_score', 'custom_interview_score', 'total_score'] if f in valid_fields), None)
    if found_score:
        res["score"] = applicant_doc.get(found_score) or 0
        
    # Standard Status
    res["status"] = applicant_doc.status or "Open"
    
    # Custom Status Override
    for custom_field in ['workflow_state', 'one_fm_applicant_status']:
        if custom_field in valid_fields:
            custom_status = applicant_doc.get(custom_field)
            if custom_status in ["Accepted", "Job Offer Issued", "Shortlisted", "Hired", "Hold", "Rejected"]:
                res["status"] = custom_status
            
    # Fetch Dynamic Matrix
    # NEW logic: Search for Nationality Evaluation Matrix first (Template-based)
    # OLD logic: Fall back to Interview Round (HRMS-based)
    
    applicant_designation = applicant_doc.get('designation') or applicant_doc.get('one_fm_designation')
    
    matrix_data = []
    
    # 1. Try NEW Nationality Evaluation Matrix
    if applicant_designation and nationality:
        # Step A: Find the Template for this designation
        template = frappe.db.get_value("Interview Evaluation Template", {"designation": applicant_designation}, "name")
        if template:
            # Step B: Find the Weightage record for this template and nationality
            weight_record = frappe.db.get_value("Nationality Evaluation Matrix", {
                "template": template,
                "nationality": nationality
            }, "name")
            
            if weight_record:
                matrix_doc = frappe.get_doc("Nationality Evaluation Matrix", weight_record)
                for w in matrix_doc.weights:
                    matrix_data.append({
                        "category": w.category or "General",
                        "category_weight": "", # Optional category total can be added here
                        "question": w.question,
                        "weight": w.weight or 0,
                        "ratings": [
                            "Excellent",
                            "Good",
                            "Average",
                            "Fair",
                            "Poor"
                        ]
                    })

    # 2. Fallback to Interview Round if matrix_data is still empty
    if not matrix_data and applicant_designation:
        interview_round = None
        if nationality:
            interview_round = frappe.db.get_value("Interview Round", {
                "designation": applicant_designation,
                "one_fm_nationality": nationality
            }, "name")
        
        if not interview_round:
            interview_round = frappe.db.get_value("Interview Round", {
                "designation": applicant_designation
            }, "name")
            
        if not interview_round:
            interview_round = frappe.db.get_value("Interview Round", {
                "round_name": applicant_designation
            }, "name")

        if interview_round:
            round_doc = frappe.get_doc("Interview Round", interview_round)
            if round_doc.get("interview_question"):
                for q in round_doc.interview_question:
                    matrix_data.append({
                        "category": q.get("category") or "General",
                        "category_weight": q.get("category_weight") or "",
                        "question": q.questions,
                        "weight": q.weight or 0,
                        "ratings": [
                            q.answer_5 or "Excellent",
                            q.answer_4 or "Good",
                            q.answer_3 or "Average",
                            q.answer_2 or "Poor",
                            q.answer_1 or "Very Poor"
                        ]
                    })
    
    res["matrix"] = matrix_data
    
    # Check for Job Offers
    try:
        offers = frappe.get_all('Job Offer', filters={'job_applicant': applicant, 'docstatus': ['<', 2]}, fields=['name'])
        res["job_offers"] = len(offers)
        if len(offers) == 1:
            res["job_offer_id"] = offers[0].name
    except Exception:
        res["job_offers"] = 0
        
    return res

@frappe.whitelist()
def save_interview_data(applicant, score, remarks, status):
    """
    Safely saves interview results using discovered field names.
    """
    valid_fields = get_valid_fields()
    # Handle status - If Shortlisted, update one_fm_applicant_status, else update status
    if status == "Shortlisted":
        update_dict = {"one_fm_applicant_status": "Shortlisted"}
    else:
        update_dict = {"status": status}
    
    # Discovery for Score
    score_fields = ['interview_score', 'custom_interview_score', 'total_score']
    found_score = next((f for f in score_fields if f in valid_fields), None)
    if found_score:
        update_dict[found_score] = score
        
    # Discovery for Remarks
    remarks_fields = ['interview_remarks', 'remarks', 'custom_remarks', 'notes']
    found_remarks = next((f for f in remarks_fields if f in valid_fields), None)
    if found_remarks:
        update_dict[found_remarks] = remarks
        
    # Use get_doc and save to trigger hooks (like magic links for Accepted)
    doc = frappe.get_doc("Job Applicant", applicant)
    doc.update(update_dict)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return "Success"

@frappe.whitelist()
def get_applicant_list():
    """
    Returns the list of applicants with discovered score fields.
    """
    valid_fields = get_valid_fields()
    # Fields that are guaranteed to exist
    fields = ['name', 'applicant_name', 'status']
    
    # Discovery for Score
    score_fields = ['interview_score', 'custom_interview_score', 'total_score']
    found_score = next((f for f in score_fields if f in valid_fields), None)
    
    if found_score:
        fields.append(f"{found_score} as interview_score")
    
    for custom_field in ['workflow_state', 'one_fm_applicant_status']:
        if custom_field in valid_fields:
            fields.append(custom_field)
            
    applicants = frappe.get_all('Job Applicant', fields=fields, limit=100, order_by='creation desc')
    
    # Override standard status with custom status to ensure UI correctly reflects Accepted
    for app in applicants:
        for custom_field in ['workflow_state', 'one_fm_applicant_status']:
            if app.get(custom_field) in ["Accepted", "Job Offer Issued", "Shortlisted", "Hired", "Hold", "Rejected"]:
                app['status'] = app[custom_field]
                
    return applicants

