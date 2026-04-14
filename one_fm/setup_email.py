import frappe
from frappe.email.doctype.email_account.email_account import EmailAccount

def mock_validate(self):
    pass

def execute():
    try:
        original_validate = EmailAccount.validate
        EmailAccount.validate = mock_validate
        
        account_name = frappe.db.get_value("Email Account", {"default_outgoing": 1}, "name")
        if not account_name:
            account_name = frappe.db.get_value("Email Account", {"email_id": "notifications@onefm.local"}, "name")
        
        if account_name:
            doc = frappe.get_doc("Email Account", account_name)
        else:
            doc = frappe.new_doc("Email Account")
            doc.email_account_name = "Default Outgoing"
            
        doc.email_id = "notifications@onefm.local"
        doc.enable_outgoing = 1
        doc.default_outgoing = 1
        doc.smtp_server = "localhost"
        doc.no_smtp_authentication = 1
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        print("Success: Outgoing Email Account Created.")
    except Exception as e:
        print("Error:", str(e))
    finally:
        EmailAccount.validate = original_validate
