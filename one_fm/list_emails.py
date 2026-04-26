import frappe
def run():
    print(frappe.get_all('Email Account', fields=['name', 'email_id', 'enable_outgoing', 'default_outgoing']))
run()
