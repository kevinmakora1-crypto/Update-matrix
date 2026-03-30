import frappe

def calculate_matrix_weights(doc, method):
    """
    Automatically populates answer_1 through answer_5 based on the weight
    using the 100/80/60/40/20 distribution seen in the Nepal matrix.
    """
    if doc.get("interview_question"):
        for q in doc.interview_question:
            if q.weight:
                try:
                    w = float(q.weight)
                    # Row 1 (Excellent/5) = 100%
                    # Row 2 (Good/4) = 80%
                    # Row 3 (Average/3) = 60%
                    # Row 4 (Fair/2) = 40%
                    # Row 5 (Poor/1) = 20%
                    
                    q.answer_5 = str(round(w, 1))
                    q.answer_4 = str(round(w * 0.8, 1))
                    q.answer_3 = str(round(w * 0.6, 1))
                    q.answer_2 = str(round(w * 0.4, 1))
                    q.answer_1 = str(round(w * 0.2, 1))
                except (ValueError, TypeError):
                    pass
