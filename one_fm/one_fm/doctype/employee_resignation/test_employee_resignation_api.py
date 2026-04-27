import frappe
from frappe.tests.utils import FrappeTestCase
from one_fm.api.v1.resignation import create_resignation

class TestEmployeeResignation(FrappeTestCase):
    def test_create_resignation_invalid_attachment(self):
        # Testing invalid base64 attachment parsing
        with self.assertRaises(Exception):
            create_resignation(
                employee_id="invalid",
                resignation_initiation_date="2026-04-27",
                relieving_date="2026-05-27",
                attachment={"attachment": "not_a_valid_base64_string"}
            )
