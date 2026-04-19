import frappe
from frappe.utils import get_site_name
from frappe.auth import LoginManager

def run():
    from one_fm.api.v1.resignation import create_resignation
    
    # Setup test context exactly like the user's execution context
    frappe.init(site="onefm.local")
    frappe.connect()
    
    # Recreate the exact mobile payload:
    payload = {
        "employee_id": "HR-EMP-02438",
        "supervisor": "Administrator",
        "attachment": '{"attachment_name":"2.jpg","attachment":"/9j/4AAQSkZJRgABC..."}'
    }
    
    try:
        frappe.set_user("Administrator")
        # Call the modified function via named arguments mimicking the POST dictionary mapping
        result = create_resignation(**payload)
        frappe.db.commit()
        print(f"SUCCESS: {result}")
    except Exception as e:
        import traceback
        print("CRASH TRACEBACK:")
        traceback.print_exc()
        
    frappe.destroy()
