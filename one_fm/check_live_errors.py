import frappe
from frappe.utils import now_datetime, add_to_date

def run():
    five_mins_ago = add_to_date(now_datetime(), minutes=-10)
    errors = frappe.get_all('Error Log', filters={'creation': ['>', five_mins_ago]}, fields=['name', 'error', 'creation'], order_by='creation desc')
    for e in errors:
        print(f"--- ERROR: {e.name} ({e.creation}) ---")
        print(e.error[:2000])
run()
