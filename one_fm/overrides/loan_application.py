import frappe
from frappe import _
from frappe.utils import flt, add_years, nowdate, getdate

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
            frappe.throw(_(f"{employee.get('employee_name')}'s salary is more than the loan application salary threshold. Only employees earning less than {max_salary_threshold} are eligible for loan."))

        # 3. Validate monthly salary against loan amount
        if monthly_salary < flt(self.loan_amount):
            frappe.throw(_(f"Loan Amount cannot exceed Employee's monthly gross salary of {monthly_salary}"))

        # 4. Validate no loan granted in last 2 years
        recent_loan = frappe.db.get_value(
            "Loan Application",
            {
                "applicant_type": "Employee",
                "applicant": employee.name,
                "company": self.company,
                "docstatus": 1,
            },
            ["name", "posting_date"],
            order_by="posting_date desc"
        )
        if recent_loan and recent_loan[1]:
            last_loan_date = recent_loan[1]
            next_eligible_date = add_years(last_loan_date, 2)
            if next_eligible_date > getdate(nowdate()):
                frappe.throw(_(
                    f"Employee does not qualify for a Loan until {next_eligible_date}."
                ))
                
        # 5. Validate annual leave balance is at least half of allocation
        self.validate_annual_leave_balance(employee.name)

    def get_employee_monthly_salary(self, employee):
        ssa = frappe.db.get_value(
            "Salary Structure Assignment",
            {"employee": employee, "docstatus": 1},
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
            frappe.throw(_(f"Insufficient Annual Leave Balance. Employee needs to have at least annual leave balance of {flt(allocation) / 2} days."))
