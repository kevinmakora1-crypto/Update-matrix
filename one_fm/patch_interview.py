import frappe

def run():
    doc_name = "HR-INT-2026-0138"
    is_exist = frappe.db.exists("Interview", doc_name)
    print(f"Exists natively check: {is_exist}")
    
    if not is_exist:
        # Search by partial name to see if there's a typo like trailing space
        matches = frappe.db.get_list("Interview", filters={"name": ["like", "%HR-INT-2026-013%"]})
        print(f"Partial matches: {matches}")
        if matches:
            doc_name = matches[0].name
            
    try:
        if frappe.db.exists("Interview", doc_name):
            has_admin = frappe.db.get_list("Interview Detail", filters={"parent": doc_name, "parenttype": "Interview", "interviewer": "Administrator"})
            if not has_admin:
                new_row = frappe.new_doc("Interview Detail")
                new_row.parent = doc_name
                new_row.parenttype = "Interview"
                new_row.parentfield = "interview_details"
                new_row.interviewer = "Administrator"
                new_row.db_insert()
                frappe.db.commit()
                print(f"Successfully patched target interview document: {doc_name}")
            else:
                print("Administrator is already present inside that Interview!")
    except Exception as e:
        print(f"Error: {e}")
