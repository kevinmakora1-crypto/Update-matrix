import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate
from datetime import date
frappe.local.flags.ignore_chart_of_accounts = 1
# SUT
from one_fm.api.tasks import assign_am_shift

frappe.flags.in_test = 1  # ensure test mode for all operations


def _get_or_create(dt, name=None, fields=None):
    try:
        fields = fields or {}
        if name and frappe.db.exists(dt, name):
            print("Using existing document:", dt, name)
            return frappe.get_doc(dt, name)
        else:
            print("Creating new document:", dt)
            doc = frappe.get_doc({"doctype": dt, **fields})
            doc.insert()
        # tests may run on lean fixtures; relax permissions/mandatory to create minimal graph
        print("Document created:", doc.doctype, doc.name)
        return doc
    except frappe.ValidationError as e:
        if "already exists" in str(e):
            return frappe.get_doc(dt, name)
        else:
            raise e


class TestShiftAssignment(FrappeTestCase):
    def setUp(self):
        # Company + Holiday List (common prerequisites for HR docs)
        self.company = _get_or_create(
            "Company",
            name="Test One FM Co.",
            fields={
                "abbr": "TOF",
                "country": "Kuwait",
                "company_name": "Test One FM Co.",
                "default_currency": "KWD",
            },
        )
        self.holiday_list = _get_or_create(
            "Holiday List",
            name="Test Custom Holiday List",
            fields={"holiday_list_name":"Test Custom Holiday List","from_date": "2025-01-01", "to_date": "2025-12-31", "total_holidays": 0},
        )
        if not self.company.get("default_holiday_list"):
            frappe.db.set_value("Company", self.company.name, "default_holiday_list", self.holiday_list.name)

        # Department
        self.department = _get_or_create(
            "Department",
            name="Security Operations - TOF",
            fields={"department_code":"RANDO1234","department_name": "Security Operations","company": self.company.name},
        )

        # Shift Type (AM)
        # Create both "AM" and "AM Shift" names for robustness across implementations
        self.shift_type = _get_or_create(
            "Shift Type",
            name="Day|07:00:00-17:00:00|9 hours",
            fields={"shift_type_name": "AM",
                "start_time": "07:00:00",
                "duration":9,
                "edit_start_time_and_end_time":0,
                "shift_type":"Day",
                "end_time": "17:00:00"},
        )
        if not frappe.db.exists("Shift Type", "AM Shift"):
            _get_or_create(
                "Shift Type",
                name="Day|09:00:00-18:00:00|10 hours",
                fields={"shift_type_name": "AM Shift",
                "start_time": "09:00:00",
                "duration":10,
                "edit_start_time_and_end_time":0,
                "shift_type":"Day",
                "end_time": "18:00:00"},
            )

        # Project
        self.project = _get_or_create(
            "Project",
            name="PROJ-0001",
            fields={"project_name": "Main Gate Project", "company": self.company.name, "is_active": "Yes"},
        )

        
        #Contact for POS in Ops Site
        self.poc_contact = _get_or_create(
            "Contact",
            name="OPS Site Contact",
            fields={
                "first_name": "OPS Site Contact",
                "last_name": "Contact",
                "designation": "Site Manager"}
        )
        # Operations Site
        self.operations_site = _get_or_create(
            "Operations Site",
            name="Main Gate",
            fields={"company": self.company.name,
                    "project": self.project.name,
                    "site_name": "Main Gate",
                    "status": "Active",
                    "poc":[{
                        'poc': self.poc_contact.name,
                        'designation': 'Site Manager',
                        'visit_frequency': 'Daily',
                    }]
                    },
        )
        self.service_type = _get_or_create(
            "Service Type",
            name="Security",
            fields={
                "service_type": "Security"
            },
        )
        # Operations Shift (link Site + Role + Project)
        
        #Item Groups and Service Items
        self.base_item_group = _get_or_create(
            "Item Group",
            name="All Item Groups",
            fields={"item_group_name": "All Item Groups",
                    "is_group": 1,
                    "parent_item_group": "",
                    "one_fm_item_group_abbr": "AIG"},
        )
        self.item_group = _get_or_create(
            "Item Group",
            name="Service",
            fields={"item_group_name": "Service",
                    "is_group": 1,
                    "parent_item_group": self.base_item_group.name,
                    "one_fm_item_group_abbr": "SVC"},
        )
        self.item_sub_group = _get_or_create(
            "Item Group",
            name="Security Services - Guard",
            fields={"item_group_name": "Security Services - Guard",
                    "is_group": 0,
                    "parent_item_group": self.item_group.name,
                    "one_fm_item_group_abbr": "SSG"},
        )
        self.item_type = _get_or_create(
            "Item Type",
            name="Security Services - Guard",
            fields={"item_type": "Security Items",
                    },
        )
        self.service_item = _get_or_create(
            "Item",
            name="Guard Service",
            fields={
                "item_name": "Guard Service",
                "item_code": "Guard Service",
                "item_type": self.item_type.name,
                "item_group": self.item_sub_group.name,
                "subitem_group":  self.item_group.name, 
                "service_type": self.service_type.name,
                "is_stock_item": 0,
                "stock_uom":"Nos",
                "is_sales_item": 1,
                "is_purchase_item": 0,
                "default_unit_of_measure": "Nos",
                "standard_rate": 100.00,
            },
        )
        self.operations_shift = _get_or_create(
            "Operations Shift",
            name="Main Gate - Guard - AM",
            fields={
                "service_type": self.service_type.name,
                "shift_number": 1,
                "company": self.company.name,
                "project": self.project.name,
                "site": self.operations_site.name,
                "operations_site": self.operations_site.name,
                
                "shift_type": self.shift_type.name,
            },
        )
        
        # Operations Role
        self.operations_role = _get_or_create(
            "Operations Role",
            name="Guard",
            fields={"company": self.company.name,
                    "project": self.project.name,
                    "post_name": "Guard",
                    "post_abbrv": "G",
                    "sale_item": self.service_item.name,
                    "site": self.operations_site.name,
                    "shift": self.operations_shift.name,
                    "shift_type": self.shift_type.name
                    }
        )
       
        #Create Employment Type
        self.employment_type = _get_or_create(
            "Employment Type",
            name="Full-time",
            fields={
                "employee_type_name": "Full-time",
            }
        )
        # Employee
        self.employee = _get_or_create(
            "Employee",
            fields={
            "first_name": "Alice",
            "one_fm_first_name_in_arabic": "أليس",
            "last_name": "Sample Last",
            "one_fm_last_name_in_arabic": "عينة",
            "company": self.company.name,
            "department": self.department.name,
            "date_of_birth": "1990-01-01",
            "date_of_joining": "2020-01-01",
            "gender": "Female",
            "status": "Active",
            "naming_series": "HR-EMP-",
            "employment_type": self.employment_type.name,
            "one_fm_basic_salary": 100
            },
        )

        # Target date for assignment
        self.shift_date = getdate()
        self.employee_schedule = _get_or_create(
            "Employee Schedule",
            name=f"{self.employee.name} - {self.shift_date}",
            fields={
                "employee": self.employee.name,
                "date": self.shift_date,
                "employee_availability": "Working",
                "operations_role": self.operations_role.name,
                "shift_type": self.shift_type.name,
                "operations_shift": self.operations_shift.name,
                "roster_type": "Basic",
            },
        )
        self.employee_schedule.save()

    def tearDown(self):
        # Clean up in reverse dependency order where possible; ignore errors if doctypes differ
        for dt, name in [
            ("Shift Assignment", None),  # bulk delete by filters below
        ]:
            try:
                if name:
                    frappe.delete_doc(dt, name, force=1, ignore_permissions=True)
            except Exception:
                pass

        # Delete test shift assignments created for the employee on the test date
        try:
            frappe.db.delete(
                "Shift Assignment",
                {
                    "employee": self.employee.name,
                    "start_date": self.shift_date,
                },
            )
        except Exception:
            pass

        for doc in [
            "Operations Shift",
            "Operations Site",
            "Operations Role",
            "Project",
            "Shift Type",
            "Department",
            "Holiday List",
            "Employee",
            "Company",
        ]:
            try:
                # delete only our records (by name)
                for name in [
                    getattr(self, "operations_shift", None) and self.operations_shift.name,
                    getattr(self, "operations_site", None) and self.operations_site.name,
                    getattr(self, "operations_role", None) and self.operations_role.name,
                    getattr(self, "project", None) and self.project.name,
                    "AM",
                    "AM Shift",
                    getattr(self, "department", None) and self.department.name,
                    getattr(self, "holiday_list", None) and self.holiday_list.name,
                    getattr(self, "employee", None) and self.employee.name,
                    getattr(self, "company", None) and self.company.name,
                ]:
                    if name and frappe.db.exists(doc, name):
                        frappe.delete_doc(doc, name, force=1, ignore_permissions=True)
            except Exception:
                pass

    def test_successful_assignment(self):
        # Act
        assign_am_shift()

        # Assert: Shift Assignment exists (submitted)
        exists = frappe.db.exists(
            "Shift Assignment",
            {"employee": self.employee.name, "start_date": self.shift_date, "docstatus": 1},
        )
        self.assertTrue(exists, "Expected a submitted Shift Assignment to be created.")

        sa = frappe.get_doc("Shift Assignment", exists)

        # shift_type should be our AM (either "AM" or "AM Shift")
        self.assertIn(sa.shift_type, {"AM", "AM Shift"}, "Shift Type should be AM/AM Shift.")
        self.assertEqual(sa.docstatus, 1, "Shift Assignment must be submitted.")
        self.assertEqual(sa.employee, self.employee.name)

        # Company should match Employee's company if present
        if hasattr(sa, "company"):
            self.assertEqual(sa.company, self.company.name)

        # Project assertion only if the field exists on Shift Assignment in this instance
        if frappe.get_meta("Shift Assignment").has_field("project"):
            self.assertEqual(sa.project, self.project.name)

    # def test_assignment_for_existing_shift(self):
    #     # First assignment succeeds
    #     assign_am_shift()

    #     # Second attempt should not create duplicate; it may raise or silently skip
    #     raised = False
    #     try:
    #         assign_am_shift()
    #     except frappe.ValidationError:
    #         raised = True

    #     # Count of assignments for that employee + date must remain 1
    #     count = frappe.db.count(
    #         "Shift Assignment",
    #         filters={"employee": self.employee.name, "start_date": self.shift_date},
    #     )
    #     self.assertEqual(count, 1, "Duplicate Shift Assignment was created.")
    #     # It's acceptable if the implementation raises to prevent duplicates
    #     # Ensure at least one of the safeguards occurred
    #     self.assertTrue(raised or count == 1)