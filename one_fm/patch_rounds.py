import frappe
def run():
    rounds = frappe.get_all("Interview Round", pluck="name")
    patched = 0
    for rn in rounds:
        has_admin = frappe.db.get_list("Interview Detail", filters={"parent": rn, "parenttype": "Interview Round", "interviewer": "Administrator"})
        if not has_admin:
            new_row = frappe.new_doc("Interview Detail")
            new_row.parent = rn
            new_row.parenttype = "Interview Round"
            new_row.parentfield = "interviewers"
            new_row.interviewer = "Administrator"
            new_row.db_insert()
            patched += 1
    frappe.db.commit()
    print(f"Patched {patched} Interview Rounds")
