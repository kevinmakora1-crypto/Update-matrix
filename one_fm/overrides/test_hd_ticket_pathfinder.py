import frappe
import unittest
from one_fm.overrides.hd_ticket import create_pathfinder_log

class TestHDTicketPathfinder(unittest.TestCase):
    def setUp(self):
        # Create a dummy HD Ticket
        self.hd_ticket = frappe.get_doc({
            "doctype": "HD Ticket",
            "subject": "Test Ticket for Pathfinder Log",
            "description": "Test Description",
            "ticket_type": "Enhancement",
            "status": "Open",
            "priority": "Medium",
            "raised_by": "Administrator" 
        }).insert(ignore_permissions=True)
        
        # Ensure roles exist
        if not frappe.db.exists("Role", "Business Analyst"):
            frappe.get_doc({"doctype": "Role", "role_name": "Business Analyst"}).insert()
        if not frappe.db.exists("Role", "Process Owner"):
            frappe.get_doc({"doctype": "Role", "role_name": "Process Owner"}).insert()
            
    def tearDown(self):
        frappe.delete_doc("HD Ticket", self.hd_ticket.name, ignore_permissions=True)
        frappe.db.sql("DELETE FROM `tabPathfinder Log` WHERE hd_ticket = %s", self.hd_ticket.name)

    def test_create_pathfinder_log_permission(self):
        # Test with no roles
        frappe.set_user("Guest")
        with self.assertRaises(frappe.PermissionError):
             create_pathfinder_log(self.hd_ticket.name)
        
        # Test with Business Analyst role
        user = "test_ba@example.com"
        if not frappe.db.exists("User", user):
            frappe.get_doc({
                "doctype": "User",
                "email": user,
                "first_name": "Test BA",
                "roles": [{"role": "Business Analyst"}]
            }).insert(ignore_permissions=True)
        
        frappe.set_user(user)
        log_name = create_pathfinder_log(self.hd_ticket.name)
        self.assertTrue(frappe.db.exists("Pathfinder Log", log_name))
        
        # Clean up log for next test
        frappe.delete_doc("Pathfinder Log", log_name, ignore_permissions=True)

        # Test with Process Owner role
        user_po = "test_po@example.com"
        if not frappe.db.exists("User", user_po):
            frappe.get_doc({
                "doctype": "User",
                "email": user_po,
                "first_name": "Test PO",
                "roles": [{"role": "Process Owner"}]
            }).insert(ignore_permissions=True)
            
        frappe.set_user(user_po)
        log_name_po = create_pathfinder_log(self.hd_ticket.name)
        self.assertTrue(frappe.db.exists("Pathfinder Log", log_name_po))

    def test_create_duplicate_log(self):
        frappe.set_user("Administrator")
        # Assign roles to Administrator for testing
        user = frappe.get_doc("User", "Administrator")
        user.add_roles("Business Analyst")
        
        log_name = create_pathfinder_log(self.hd_ticket.name)
        
        with self.assertRaises(frappe.ValidationError):
            create_pathfinder_log(self.hd_ticket.name)
