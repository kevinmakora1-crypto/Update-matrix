from frappe.tests.utils import FrappeTestCase
import frappe
from datetime import datetime
import calendar

class TestEmployeeMonthlyAction(FrappeTestCase):
    def setUp(self):
        # Get existing employee by employee_number
        employee_name = frappe.get_value("Employee", {"name": "HR-EMP-00001"}, "name")
        if not employee_name:
            frappe.throw("Test Employee with name 'EMP-0001' does not exist.")
        self.test_employee = frappe.get_doc("Employee", employee_name)

        # Get current month and year
        today_date = datetime.today()
        current_month_name = today_date.strftime("%B")
        current_year = str(today_date.year)


        self.goals = self.get_employee_goals(
            employee=self.test_employee.name,
            year=current_year,
            month=current_month_name
        )

        if len(self.goals) < 2:
            frappe.throw("Not enough goals found for the employee in the current month.")

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
        if self.employee_monthly_action.docstatus == 1:
            self.employee_monthly_action.cancel()

        if self.employee_monthly_action:
            frappe.delete_doc("Employee Monthly Action", self.employee_monthly_action.name, force=True)

    def get_employee_goals(self, employee, year, month):
        if not employee or not year or not month:
            return []
        month_index = list(calendar.month_name).index(month)
        year = int(year)
        from_date = datetime(year, month_index, 1).date()
        last_day = calendar.monthrange(year, month_index)[1]
        to_date = datetime(year, month_index, last_day).date()

        goals = frappe.get_all(
            "Goal",
            filters={
                "employee": employee,
                "start_date": ["<=", to_date],
                "end_date": [">=", from_date]
            },
            fields=["name", "goal_name", "progress"]
        )
        return goals

    def test_on_submit_updates_goal_progress(self):
        self.employee_monthly_action.submit()

        updated_goal_1_progress = frappe.get_value("Goal", self.goals[0]["name"], "progress")
        updated_goal_2_progress = frappe.get_value("Goal", self.goals[1]["name"], "progress")

        self.assertEqual(updated_goal_1_progress, 50)
        self.assertEqual(updated_goal_2_progress, 75)
