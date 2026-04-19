import frappe

def execute():
    doctypes = [
        "Candidate Country Process", 
        "Overseas Medical Appointment WAFID", 
        "Overseas Remedical", 
        "PCC Clearance", 
        "Visa Stamping", 
        "Arrival and Deployment"
    ]
    
    for dt in doctypes:
        doc = frappe.get_doc("DocType", dt)
        if not doc.title_field:
            doc.title_field = "candidate_name"
        
        doc.search_fields = "candidate_name,passport_number"
        doc.show_title_field_in_link = 1
        
        # Saving the DocType automatically updates both the database and the JSON files
        doc.save(ignore_permissions=True)
        print(f"Updated {dt}: title_field=candidate_name, search_fields=candidate_name,passport_number")
    
    frappe.db.commit()
