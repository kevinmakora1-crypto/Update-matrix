import frappe
import unittest

class TestUserMobileUnsetOnDisable(unittest.TestCase):
    def setUp(self):
        # Create a new test user with mobile set
        self.test_user = frappe.get_doc({
            "doctype": "User",
            "email": "test_disable_user@example.com",
            "first_name": "Test",
            "enabled": 1,
            "mobile_no": "9898989898"
        })
        self.test_user.insert(ignore_permissions=True)

    def test_mobile_unset_when_user_disabled(self):
        # Disable the user
        self.test_user.enabled = 0
        self.test_user.save(ignore_permissions=True)
        # Reload from DB to verify
        user = frappe.get_doc("User", self.test_user.name)
        self.assertEqual(user.mobile_no, "" or None, "Mobile should be unset when user is disabled.")

    def tearDown(self):
        # Delete the test user
        frappe.delete_doc("User", self.test_user.name, ignore_permissions=True)