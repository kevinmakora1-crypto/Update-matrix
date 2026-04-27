import frappe
from frappe.tests.utils import FrappeTestCase
from one_fm.api.v1.utils import resolve_active_user

class TestApiUtils(FrappeTestCase):
    def setUp(self):
        # Create a dummy employee to act as our primary user
        if not frappe.db.exists("Employee", "HR-EMP-00001"):
            doc = frappe.get_doc({
                "doctype": "Employee",
                "employee": "HR-EMP-00001",
                "first_name": "Test",
                "status": "Active"
            })
            doc.flags.ignore_mandatory = True
            doc.insert(ignore_permissions=True)
            
    def test_resolve_active_user_no_leave(self):
        # User is not on leave, should return the same user
        user = resolve_active_user("Administrator")
        self.assertEqual(user, "Administrator")
