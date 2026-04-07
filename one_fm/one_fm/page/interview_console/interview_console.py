import frappe
from frappe.utils import getdate, nowdate

ALLOWED_ROLES = {"System Manager", "HR Manager", "Interviewer", "HR User", "Recruiter", "Senior Recruiter"}

def _check_console_access():
    """Check if the current user has at least one allowed role."""
    if not ALLOWED_ROLES.intersection(set(frappe.get_roles())):
        frappe.throw("You are not permitted to access this console.", frappe.PermissionError)

def get_valid_fields():
    meta = frappe.get_meta('Job Applicant')
    return [df.fieldname for df in meta.fields]

def _ensure_skill_exists(skill_name):
    """Create a Skill document if it doesn't exist, return the skill name."""
    if not skill_name:
        skill_name = "General"
    # Truncate to max 140 chars (Frappe Link field limit)
    skill_name = skill_name[:140]
    if not frappe.db.exists("Skill", skill_name):
        try:
            frappe.get_doc({
                "doctype": "Skill",
                "skill_name": skill_name
            }).insert(ignore_permissions=True)
        except frappe.DuplicateEntryError:
            pass
    return skill_name

@frappe.whitelist()
def get_applicant_data(applicant, interview_round_name=None):
    """
    Returns age, remarks, score, status, and dynamic interview matrix.
    """
    _check_console_access()
    valid_fields = get_valid_fields()
    res = {"age": "--", "height": "", "remarks": "", "score": 0, "status": "Open", "matrix": [], "feedbacks": [], "feedback_count": 0, "available_rounds": []}
    
    # Fetch Applicant details
    applicant_doc = frappe.get_doc('Job Applicant', applicant)
    designation = applicant_doc.designation
    nationality = applicant_doc.get('one_fm_nationality')

    # Height
    res["height"] = applicant_doc.get('one_fm_height') or ""

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
        
    # Fetch score as AVERAGE of all Interview Feedback scores for this applicant
    all_feedbacks = frappe.get_all("Interview Feedback",
        filters={"job_applicant": applicant, "docstatus": 1},
        fields=["name", "interviewer", "average_rating", "result", "custom_remarks", "creation"],
        order_by="creation desc"
    )
    all_interviews = frappe.db.count("Interview", {"job_applicant": applicant, "docstatus": ["<", 2]})
    res["interview_count"] = all_interviews
    
    res["feedback_count"] = len(all_feedbacks)
    res["feedbacks"] = all_feedbacks

    if all_feedbacks:
        # Compute score as average of all non-null Interview Feedback ratings
        ratings = [fb.get("average_rating") for fb in all_feedbacks if fb.get("average_rating") is not None]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            res["score"] = round(avg_rating * 100)
        else:
            res["score"] = 0
    else:
        res["score"] = 0
        
    # Standard Status
    res["status"] = applicant_doc.status or "Open"
    
    # Custom Status Override
    for custom_field in ['workflow_state', 'one_fm_applicant_status']:
        if custom_field in valid_fields:
            custom_status = applicant_doc.get(custom_field)
            if custom_status in ["Accepted", "Job Offer Issued", "Shortlisted", "Hired", "Hold", "Rejected"]:
                res["status"] = custom_status
            
    # Fetch Dynamic Matrix from Interview Round
    applicant_designation = applicant_doc.get('designation') or applicant_doc.get('one_fm_designation')
    
    # Gather ALL available rounds for this designation to populate the UI dropdown
    if applicant_designation:
        available_rounds = frappe.get_all("Interview Round", filters={"designation": applicant_designation}, pluck="name")
        res["available_rounds"] = available_rounds

    matrix_data = []
    interview_round = None
    
    if interview_round_name:
        interview_round = interview_round_name
        round_doc = frappe.get_doc("Interview Round", interview_round)
        
        matrix_map = {}
        if round_doc.get("interview_matrix"):
            for m in round_doc.interview_matrix:
                if m.question:
                    matrix_map[m.question] = {
                        "score_5": m.score_5 or "",
                        "score_4": m.score_4 or "",
                        "score_3": m.score_3 or "",
                        "score_2": m.score_2 or "",
                        "score_1": m.score_1 or ""
                    }

        if round_doc.get("interview_question"):
            for q in round_doc.interview_question:
                ans = matrix_map.get(q.questions, {})
                matrix_data.append({
                    "category": q.get("category") or "General",
                    "category_weight": q.get("category_weight") or "",
                    "question": q.questions,
                    "weight": q.weight or 0,
                    "ratings": [
                        ans.get("score_5", q.answer_5 or "Excellent"),
                        ans.get("score_4", q.answer_4 or "Good"),
                        ans.get("score_3", q.answer_3 or "Average"),
                        ans.get("score_2", q.answer_2 or "Poor"),
                        ans.get("score_1", q.answer_1 or "Very Poor")
                    ]
                })
        
        res["matrix"] = matrix_data
        res["interview_round"] = interview_round
    else:
        # If no round explicitly requested, leave matrix empty so UI shows the empty state graphic
        res["matrix"] = []
        res["interview_round"] = None
    
    # Check for Job Offers
    try:
        offers = frappe.get_all('Job Offer', filters={'job_applicant': applicant, 'docstatus': ['<', 2]}, fields=['name'])
        res["job_offers"] = len(offers)
        if len(offers) == 1:
            res["job_offer_id"] = offers[0].name
    except Exception:
        res["job_offers"] = 0
    try:
        res["photo_count"] = frappe.db.count("File", {"attached_to_doctype": "Job Applicant", "attached_to_name": applicant})
    except Exception:
        res["photo_count"] = 0
        
    return res

@frappe.whitelist()
def save_interview_data(applicant, score, remarks, status, scores_detail=None, interview_round=None, height=None, photo_data=None):
    """
    Saves interview results by creating/updating an Interview document.
    Also updates Job Applicant status.
    
    Args:
        scores_detail: JSON string of [{question, category, score, weight}, ...]
        interview_round: Name of the Interview Round used
    """
    import json
    from frappe.utils import nowdate, nowtime
    _check_console_access()
    
    if photo_data:
        import base64
        try:
            head, base64_data = photo_data.split(",", 1)
            ext = head.split(";")[0].split("/")[1]
            if ext == 'jpeg': ext = 'jpg'
            
            from frappe.utils import random_string
            file_name = f"{applicant}_photo_{random_string(5)}.{ext}"
            
            _file = frappe.new_doc("File")
            _file.file_name = file_name
            _file.attached_to_doctype = "Job Applicant"
            _file.attached_to_name = applicant
            _file.content = base64.b64decode(base64_data)
            _file.is_private = 1
            _file.insert(ignore_permissions=True)
        except Exception:
            frappe.log_error(title="Interview Console Photo Error", message=frappe.get_traceback())

    valid_fields = get_valid_fields()
    
    # --- 1. Update Job Applicant Status ---
    doc = frappe.get_doc("Job Applicant", applicant)

    # Check if a Workflow is active on Job Applicant
    has_workflow = frappe.get_all("Workflow", filters={"document_type": "Job Applicant", "is_active": 1}, limit=1)

    if status == "Shortlisted":
        doc.one_fm_applicant_status = "Shortlisted"
    elif has_workflow:
        # Update workflow_state to avoid read-only status conflicts
        doc.workflow_state = status
    else:
        doc.status = status

    # Save height if provided
    if height:
        doc.one_fm_height = float(height)
    doc.save(ignore_permissions=True)
    
    # --- 2. Map console status to Interview status ---
    interview_status_map = {
        "Accepted": "Cleared",
        "Shortlisted": "Cleared",
        "Rejected": "Rejected",
        "Hold": "Under Review",
    }
    interview_status = interview_status_map.get(status, "Under Review" if int(score or 0) > 0 else "Pending")
    
    # --- 3. Parse scores detail for later use ---
    parsed_details = []
    if scores_detail:
        try:
            parsed_details = json.loads(scores_detail) if isinstance(scores_detail, str) else scores_detail
        except Exception:
            pass
    
    # --- 4. Find or Create Interview (interview_summary left blank) ---
    # --- 4. Always Create New Interview ---
    existing_interview = None
    
    if existing_interview:
        interview_doc = frappe.get_doc("Interview", existing_interview)
        
        if interview_doc.docstatus == 1:
            frappe.db.set_value("Interview", existing_interview, {
                "status": interview_status,
                "interview_summary": "",
                "interview_round": interview_round or interview_doc.interview_round
            }, update_modified=True)
        else:
            interview_doc.status = interview_status
            interview_doc.interview_summary = ""
            if interview_round:
                interview_doc.interview_round = interview_round
            interview_doc.save(ignore_permissions=True)
            if interview_doc.status in ["Cleared", "Rejected"]:
                interview_doc.submit()
    else:
        interview_doc = frappe.new_doc("Interview")
        interview_doc.interview_round = interview_round or ""
        interview_doc.job_applicant = applicant
        interview_doc.designation = doc.designation
        interview_doc.status = interview_status
        interview_doc.scheduled_on = nowdate()
        interview_doc.from_time = nowtime()
        interview_doc.to_time = nowtime()
        
        if interview_round:
            try:
                round_doc = frappe.get_doc("Interview Round", interview_round)
                for interviewer in round_doc.interviewers:
                    interview_doc.append("interview_details", {
                        "interviewer": interviewer.user
                    })
            except Exception:
                pass
        
        interview_doc.insert(ignore_permissions=True)
        if interview_doc.status in ["Cleared", "Rejected"]:
            interview_doc.submit()
    # --- 6. Auto-create/update Interview Feedback ---
    interview_name = existing_interview or interview_doc.name
    feedback_result = ""
    if status in ["Accepted", "Shortlisted"]:
        feedback_result = "Cleared"
    elif status == "Rejected":
        feedback_result = "Rejected"
    else:
        feedback_result = "Cleared" if int(score or 0) >= 50 else "Rejected"
    
    # avg_rating will be calculated from category averages after building skill_rows
    
    # Build per-category average scores for skill circles
    category_scores = {}
    for d in parsed_details:
        cat = d.get("category", "General")
        q_score = float(d.get("score", 0))
        if cat not in category_scores:
            category_scores[cat] = {"total": 0, "count": 0}
        category_scores[cat]["total"] += q_score
        category_scores[cat]["count"] += 1
    
    # Convert to list of {skill, rating} for skill_assessment
    skill_rows = []
    for cat, data in category_scores.items():
        cat_avg = data["total"] / data["count"] if data["count"] > 0 else 0
        cat_rating = cat_avg / 5.0  # Convert 0-5 score to 0-1 rating
        skill_name = _ensure_skill_exists(cat)
        skill_rows.append({"skill": skill_name, "rating": min(max(cat_rating, 0), 1)})
    
    # Calculate avg_rating from category averages (matches Feedback Summary circles)
    if skill_rows:
        avg_rating = sum(r["rating"] for r in skill_rows) / len(skill_rows)
    else:
        avg_rating = float(score or 0) / 100.0
    avg_rating = min(max(avg_rating, 0), 1)
    
    # --- 6. Clean up drafts, then create a NEW Interview Feedback ---
    # Delete any draft (docstatus=0) feedbacks from this user for this interview
    draft_feedbacks = frappe.get_all("Interview Feedback", filters={
        "interview": interview_name,
        "interviewer": frappe.session.user,
        "docstatus": 0
    }, pluck="name")
    for dfb in draft_feedbacks:
        frappe.delete_doc("Interview Feedback", dfb, force=True, ignore_permissions=True)

    fb = frappe.new_doc("Interview Feedback")
    fb.interview = interview_name
    fb.interview_round = interview_round or ""
    fb.job_applicant = applicant
    fb.interviewer = frappe.session.user
    fb.result = feedback_result
    fb.feedback = ""
    fb.custom_remarks = remarks or ""
    for row in skill_rows:
        fb.append("skill_assessment", row)
    for d in parsed_details:
        fb.append("interview_question_assessment", {
            "questions": d.get("question", ""),
            "weight": float(d.get("weight", 0)),
            "score": int(d.get("score", 0))
        })
    # Skip HRMS duplicate validation — we intentionally accumulate feedbacks
    fb.flags.ignore_validate = True
    fb.insert(ignore_permissions=True)
    fb.submit()
    fb.db_set("average_rating", avg_rating)

    # --- 7. Recalculate total score as AVERAGE of all feedbacks for this applicant ---
    all_fb_scores = frappe.get_all("Interview Feedback",
        filters={"job_applicant": applicant, "docstatus": 1},
        fields=["average_rating"]
    )
    if all_fb_scores:
        avg_all = sum(f.average_rating or 0 for f in all_fb_scores) / len(all_fb_scores)
        total_score = round(avg_all * 100, 0)
    else:
        avg_all = avg_rating
        total_score = float(score or 0)

    frappe.db.set_value("Interview", interview_name, {
        "average_rating": avg_all,
        "total_interview_score": total_score,
    }, update_modified=False)
    
    frappe.db.commit()
    return "Success"

@frappe.whitelist()
def clear_interview_data(applicant):
    """
    Cancels and deletes Interview Feedback and Interview documents for the applicant.
    Called when the Reset button is clicked in the Interview Console.
    """
    _check_console_access()
    # Delete feedbacks first (child reference)
    feedbacks = frappe.get_all("Interview Feedback", filters={
        "job_applicant": applicant, "docstatus": ["<", 2]
    }, fields=["name", "docstatus"])
    for fb in feedbacks:
        if fb.docstatus == 1:
            frappe.get_doc("Interview Feedback", fb.name).cancel()
        frappe.delete_doc("Interview Feedback", fb.name, force=True, ignore_permissions=True)
    
    # Delete interviews
    interviews = frappe.get_all("Interview", filters={
        "job_applicant": applicant, "docstatus": ["<", 2]
    }, fields=["name", "docstatus"])
    for iv in interviews:
        if iv.docstatus == 1:
            frappe.get_doc("Interview", iv.name).cancel()
        frappe.delete_doc("Interview", iv.name, force=True, ignore_permissions=True)
    
    # Reset Job Applicant status to Open
    doc = frappe.get_doc("Job Applicant", applicant)
    doc.status = "Open"
    doc.save(ignore_permissions=True)

    frappe.db.commit()
    return "Success"

@frappe.whitelist()
def get_applicant_list(hiring_method=None, start=0, page_length=200):
    """
    Returns the list of applicants with discovered score fields.
    Optionally filtered by hiring method (e.g., 'Bulk Recruitment').
    Supports pagination via start and page_length.
    """
    _check_console_access()
    valid_fields = get_valid_fields()
    # Fields that are guaranteed to exist
    fields = ['name', 'applicant_name', 'status', 'job_title', 'designation']
    
    for custom_field in ['workflow_state', 'one_fm_applicant_status', 'one_fm_passport_number']:
        if custom_field in valid_fields:
            fields.append(custom_field)

    filters = {}
    if hiring_method and 'one_fm_hiring_method' in valid_fields:
        filters['one_fm_hiring_method'] = hiring_method
            
    applicants = frappe.get_all('Job Applicant', fields=fields, filters=filters,
                                limit_start=int(start), limit_page_length=int(page_length),
                                order_by='creation desc')
    
    # Batch-fetch interview scores to avoid N+1 queries
    applicant_names = [app.name for app in applicants]
    interview_scores_map = {}
    if applicant_names:
        interview_rows = frappe.get_all(
            "Interview",
            filters={"job_applicant": ["in", applicant_names], "docstatus": ["<", 2]},
            fields=["job_applicant", "total_interview_score"],
        )
        for row in interview_rows:
            key = row.get("job_applicant")
            if key and key not in interview_scores_map:
                interview_scores_map[key] = row.get("total_interview_score") or 0

    # Resolve Job Opening title, apply batched scores, and override status
    for app in applicants:
        if app.get('job_title'):
            opening_title = frappe.db.get_value('Job Opening', app.job_title, 'job_title')
            app['job_opening_title'] = opening_title or app.job_title

        app['interview_score'] = interview_scores_map.get(app.name, 0)

        for custom_field in ['workflow_state', 'one_fm_applicant_status']:
            if app.get(custom_field) in ["Accepted", "Job Offer Issued", "Shortlisted", "Hired", "Hold", "Rejected"]:
                app['status'] = app[custom_field]
                
    return applicants


