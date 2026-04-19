import frappe
from one_fm.api.v1.configuration import app_service_group, app_service, user_app_service

def execute():
    frappe.set_user("mobileapp@one-fm.com")
    
    frappe.local.response = {}
    app_service_group()
    print("--- SERVICE GROUPS ---")
    print(frappe.local.response.get("data", []))

    frappe.local.response = {}
    app_service()
    print("--- ALL APP SERVICES FOR USER ---")
    print(frappe.local.response.get("data", []))
