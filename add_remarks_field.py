import frappe
frappe.init(site="onefm.local")
frappe.connect()

if frappe.db.exists("Custom Field", "Interview Feedback-custom_remarks"):
    print("Remarks field already exists")
else:
    doc = frappe.get_doc({
        "doctype": "Custom Field",
        "dt": "Interview Feedback",
        "fieldname": "custom_remarks",
        "fieldtype": "Small Text",
        "label": "Remarks",
        "insert_after": "feedback"
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print("Remarks field CREATED")

frappe.destroy()
