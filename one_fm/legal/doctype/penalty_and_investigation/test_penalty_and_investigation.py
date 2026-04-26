import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today


class TestPenaltyAndInvestigation(FrappeTestCase):
	def setUp(self):
		# Create test employee if not exists
		if not frappe.db.exists("Employee", "TEST-EMP-001"):
			self.employee = frappe.get_doc({
				"doctype": "Employee",
				"employee": "TEST-EMP-001",
				"first_name": "Test",
				"last_name": "Employee",
				"gender": "Male",
				"date_of_birth": "1990-01-01",
				"date_of_joining": "2020-01-01",
				"status": "Active",
				"company": "One Facilities Management"
			}).insert()
		else:
			self.employee = frappe.get_doc("Employee", "TEST-EMP-001")

		# Create test penalty code
		if not frappe.db.exists("Penalty Code", "TEST-PEN-001"):
			self.penalty_code = frappe.get_doc({
				"doctype": "Penalty Code",
				"penalty_name": "Test Penalty",
				"violation_type": "Work",
				"naming_series": "HR-PEN-.####",
				"is_active": 1
			}).insert()
			# Rename to predictable name if series was used
			if self.penalty_code.name != "TEST-PEN-001":
				frappe.rename_doc("Penalty Code", self.penalty_code.name, "TEST-PEN-001")
				self.penalty_code = frappe.get_doc("Penalty Code", "TEST-PEN-001")
		else:
			self.penalty_code = frappe.get_doc("Penalty Code", "TEST-PEN-001")

	def test_duplicate_penalty_validation(self):
		# 1. Create first penalty investigation
		doc1 = frappe.get_doc({
			"doctype": "Penalty And Investigation",
			"employee": self.employee.name,
			"applied_penalty_code": self.penalty_code.name,
			"incident_date": today(),
			"issuance_date": today(),
		}).insert()

		# 2. Try to create second penalty investigation with same details
		doc2 = frappe.get_doc({
			"doctype": "Penalty And Investigation",
			"employee": self.employee.name,
			"applied_penalty_code": self.penalty_code.name,
			"incident_date": today(),
			"issuance_date": today(),
		})

		self.assertRaises(frappe.ValidationError, doc2.insert)

		# 3. Cancel first and try again (should succeed)
		doc1.cancel()
		doc2.insert()
		self.assertTrue(frappe.db.exists("Penalty And Investigation", doc2.name))
