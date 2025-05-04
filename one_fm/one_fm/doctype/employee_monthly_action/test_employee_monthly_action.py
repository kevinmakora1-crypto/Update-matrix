from frappe.tests.utils import FrappeTestCase
import frappe
from datetime import datetime
import calendar

class TestEmployeeMonthlyAction(FrappeTestCase):
    def setUp(self):
        # Create a test user
        self.test_user = frappe.get_doc({
            "doctype": "User",
            "email": "test_user@example.com",
            "first_name": "Test",
            "last_name": "User",
            "enabled": 1
        }).insert(ignore_permissions=True)

        # Create a test employee
        self.test_employee = frappe.get_doc({
            "doctype": "Employee",
            "employee_number": "HR-EMP-00001",
            "employee_name": "Test Employee",
            "user_id": self.test_user.name,
            "first_name": "Test",
            "last_name": "User",
            "company": "One Facilities Management",
            "designation": "Jr. Software Developer",
            "department": "IT - ONEFM",
            "date_of_joining": "2023-01-01",
            "gender": "Male",
            "date_of_birth": "1990-01-01",
            "one_fm_first_name_in_arabic": "تجربة",
            "one_fm_last_name_in_arabic": "الموظف",
            "one_fm_basic_salary": 1000
        }).insert(ignore_permissions=True)

        # Create goals for the employee
        self.goal_1 = frappe.get_doc({
            "doctype": "Goal",
            "goal_name": "Test Goal 1",
            "employee": self.test_employee.name,
            "start_date": datetime.today().date(),
            "end_date": datetime.today().date(),
            "progress": 0
        }).insert(ignore_permissions=True)

        self.goal_2 = frappe.get_doc({
            "doctype": "Goal",
            "goal_name": "Test Goal 2",
            "employee": self.test_employee.name,
            "start_date": datetime.today().date(),
            "end_date": datetime.today().date(),
            "progress": 0
        }).insert(ignore_permissions=True)

        # Get current month and year
        today_date = datetime.today()
        current_month_name = today_date.strftime("%B")
        current_year = str(today_date.year)

        # Use the created goals
        self.goals = [
            {"goal_name": self.goal_1.goal_name, "name": self.goal_1.name, "progress": 0},
            {"goal_name": self.goal_2.goal_name, "name": self.goal_2.name, "progress": 0}
        ]

        # Create Employee Monthly Action using existing goals
        self.employee_monthly_action = frappe.get_doc({
            "doctype": "Employee Monthly Action",
            "employee": self.test_employee.name,
            "month": current_month_name,
            "year": current_year,
            "goal_update": [
                {"goal": self.goals[0]["goal_name"], "current_progress": 50},
                {"goal": self.goals[1]["goal_name"], "current_progress": 75}
            ]
        }).insert(ignore_permissions=True)

    def tearDown(self):
        # Cancel and delete the test documents
        if self.employee_monthly_action.docstatus == 1:
            self.employee_monthly_action.cancel()

        if self.employee_monthly_action:
            frappe.delete_doc("Employee Monthly Action", self.employee_monthly_action.name, force=True)

        if self.goal_1:
            frappe.delete_doc("Goal", self.goal_1.name, force=True)

        if self.goal_2:
            frappe.delete_doc("Goal", self.goal_2.name, force=True)

        if self.test_employee:
			# Remove User Permissions pointing to this Employee
            user_permissions = frappe.get_all(
				"User Permission",
				filters={"user": "test_user@example.com"},
				pluck="name"
			)
            for perm in user_permissions:
               frappe.delete_doc("User Permission", perm, force=True)
            frappe.delete_doc("Employee", self.test_employee.name, force=True)


        if self.test_user:
            frappe.delete_doc("User", self.test_user.name, force=True)
        frappe.db.commit()


    def test_on_submit_updates_goal_progress(self):
        self.employee_monthly_action.submit()

        updated_goal_1_progress = frappe.get_value("Goal", self.goals[0]["name"], "progress")
        updated_goal_2_progress = frappe.get_value("Goal", self.goals[1]["name"], "progress")

        self.assertEqual(updated_goal_1_progress, 50)
        self.assertEqual(updated_goal_2_progress, 75)
