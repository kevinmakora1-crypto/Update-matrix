import frappe

def run():
    if not frappe.db.exists("Email Account", "Dummy Local"):
        doc = frappe.get_doc({
            "doctype": "Email Account",
            "email_id": "test@localhost.com",
            "email_account_name": "Dummy Local",
            "domain": "example.com",
            "awaiting_password": 0,
            "enable_outgoing": 1,
            "default_outgoing": 1,
            "smtp_server": "localhost",
            "smtp_port": 1025,
            "no_smtp_authentication": 1,
            "add_signature": 0
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        print("Created Dummy Local email account.")
    else:
        # Just ensure it's default
        doc = frappe.get_doc("Email Account", "Dummy Local")
        doc.default_outgoing = 1
        doc.enable_outgoing = 1
        doc.smtp_server = "localhost"
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        print("Ensured Dummy Local exists and is default.")
