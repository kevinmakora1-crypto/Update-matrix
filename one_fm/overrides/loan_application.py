import frappe
from frappe import _
from frappe.utils import flt, add_years, nowdate

from lending.loan_management.doctype.loan_application.loan_application import LoanApplication



class LoanApplicationOverride(LoanApplication):
    def validate(self):
        super().validate()
        self.validate_employee_loan_eligibility() 

    def validate_employee_loan_eligibility(self):
        if self.applicant_type != "Employee":
            return

        # Get employee doc
        employee = frappe.get_doc("Employee", self.applicant)

        # 1. Validate under_company_residency
        if not employee.get("under_company_residency"):
            frappe.throw(_(f"{employee.get('employee_name')} is not under company's residency. Only employees under the company's residency are eligible for loan."))

        # 2. Validate monthly salary against maximum salary threshold in Loan Product
        max_salary_threshold = frappe.db.get_value("Loan Product", self.loan_product, "custom_maximum_salary_threshold")
        monthly_salary = self.get_employee_monthly_salary(employee.name)
        if max_salary_threshold and monthly_salary >= flt(max_salary_threshold):
            frappe.throw(_(f"{employee.get('employee_name')}'s salary is more than than the loan application salary threshold. Only employees earning less than {max_salary_threshold} are eligible for loan."))

        # 3. Validate monthly salary against loan amount
        if monthly_salary < flt(self.loan_amount):
            frappe.throw(_("Employee's monthly salary is less than the requested loan amount."))

        # 4. Validate no loan granted in last 2 years
        two_years_ago = add_years(nowdate(), -2)
        recent_loan = frappe.db.exists(
            "Loan Application",
            {
                "applicant_type": "Employee",
                "applicant": employee.name,
                "company": self.company,
                "docstatus": 1,
                "posting_date": [">=", two_years_ago],
            },
        )
        if recent_loan:
            frappe.throw(_("Employee has been granted a loan within the last two years."))

        # 5. Validate annual leave balance is at least half of allocation
        self.validate_annual_leave_balance(employee.name)

    def get_employee_monthly_salary(self, employee):
        ssa = frappe.db.get_value(
            "Salary Structure Assignment",
            {"employee": employee, "docstatus": 1, "is_active": 1},
            ["base", "salary_structure"],
            as_dict=True,
        )
        if not ssa or not ssa.base:
            frappe.throw(_("No active Salary Structure Assignment found for employee."))
        return flt(ssa.base)
    
    def validate_annual_leave_balance(self, employee):
        leave_type = "Annual Leave"
        allocation = frappe.db.get_value(
            "Leave Allocation",
            {
                "employee": employee,
                "leave_type": leave_type,
                "docstatus": 1,
            },
            "total_leaves_allocated",
        )
        if not allocation:
            frappe.throw(_("No Annual Leave allocation found for employee."))

        # Use the helper from HRMS to get current balance
        from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on
        balance = get_leave_balance_on(
            employee,
            leave_type,
            frappe.utils.nowdate()
        )

        if flt(balance) < (flt(allocation) / 2):
            frappe.throw(_("Employee's annual leave balance must be at least half of the annual leave allocation to apply for a loan."))
