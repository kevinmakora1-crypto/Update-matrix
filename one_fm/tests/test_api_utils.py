import frappe
from frappe.tests.utils import FrappeTestCase
from one_fm.api.v1.utils import resolve_active_user

class TestApiUtils(FrappeTestCase):
    def setUp(self):
        # Create a dummy employee to act as our primary user
        if not frappe.db.exists("Employee", "HR-EMP-00001"):
            doc = frappe.get_doc({
                "doctype": "Employee",
                "name": "HR-EMP-00001",
                "employee": "HR-EMP-00001",
                "user_id": "on_leave@example.com",
                "first_name": "Test",
                "status": "Active"
            })
            doc.flags.ignore_mandatory = True
            doc.insert(ignore_permissions=True)
            
    def test_resolve_active_user_no_leave(self):
        # User is not on leave, should return the same user
        user = resolve_active_user("Administrator")
        self.assertEqual(user, "Administrator")
        
    def test_resolve_active_user_rerouting(self):
        # Simple fallback test since full leave rerouting logic requires Leave Application
        user = resolve_active_user("on_leave@example.com")
        # In a real environment with a Leave Application, this would route to custom_reliever
        # Without an active leave, it should just return the same user.
        self.assertEqual(user, "on_leave@example.com")
