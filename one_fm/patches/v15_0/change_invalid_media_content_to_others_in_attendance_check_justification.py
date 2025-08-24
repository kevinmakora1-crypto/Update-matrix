import frappe

def execute():
    # Fetch all Attendance Check records with justification "Invalid media content"
    records = frappe.get_all(
        "Attendance Check",
        filters={"justification": "Invalid media content"},
        fields=["name"]
    )
    for rec in records:
        print(rec)
        # Update justification to 'Other' and set other_reason
        frappe.db.set_value("Attendance Check", rec.name, {
            "justification": "Other",
            "other_reason": "Invalid media content"
        })
    frappe.db.commit()