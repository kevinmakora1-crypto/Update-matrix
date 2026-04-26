import frappe

def fix():
    email_account_name = "Outgoing"
    if not frappe.db.exists("Email Account", email_account_name):
        doc = frappe.new_doc("Email Account")
        doc.email_id = "notifications@onefm.local"
        doc.email_account_name = email_account_name
        doc.enable_outgoing = 1
        doc.default_outgoing = 1
        doc.smtp_server = "localhost"
        doc.smtp_port = 587
        doc.append("capabilities", {"capability": "Outgoing"})
        doc.insert(ignore_permissions=True)
        print(f"Created Email Account: {email_account_name}")
    else:
        doc = frappe.get_doc("Email Account", email_account_name)
        doc.enable_outgoing = 1
        doc.default_outgoing = 1
        doc.save(ignore_permissions=True)
        print(f"Updated Email Account: {email_account_name}")
    frappe.db.commit()
