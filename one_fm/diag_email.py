import frappe
from frappe.email.doctype.email_account.email_account import EmailAccount

def run():
    print("--- Diagnostics ---")
    print(f"Site: {frappe.local.site}")
    
    # 1. Check if the record exists in DB
    record = frappe.db.get_value("Email Account", {"enable_outgoing": 1, "default_outgoing": 1}, ["name", "email_id"], as_dict=1)
    print(f"DB Record: {record}")
    
    # 2. Check find_one_by_filters
    doc = EmailAccount.find_one_by_filters(enable_outgoing=1, default_outgoing=1)
    print(f"find_one_by_filters doc: {doc.name if doc else None}")
    
    # 3. Check find_default_outgoing
    doc_default = EmailAccount.find_default_outgoing()
    print(f"find_default_outgoing doc: {doc_default.name if doc_default else None}")
    
    # 4. Check find_outgoing
    res = EmailAccount.find_outgoing(_raise_error=False)
    print(f"find_outgoing result: {res}")
    
    # 5. Mute check
    print(f"are_emails_muted: {frappe.are_emails_muted()}")
    
    # 6. Global cache
    print(f"Cache key 'outgoing_email_account' in frappe.local: {hasattr(frappe.local, 'outgoing_email_account')}")
    if hasattr(frappe.local, 'outgoing_email_account'):
        print(f"Cache value: {frappe.local.outgoing_email_account}")

run()
