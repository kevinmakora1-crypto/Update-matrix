import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate
from frappe.model.document import Document

from lending.loan_management.doctype.loan.loan import Loan




class LoanOverride(Loan):
    pass


@frappe.whitelist()
def create_additional_repayment(parent_doc, date, repayment_account, paid_amount):
    try:
        if not all([parent_doc, date, repayment_account, paid_amount]):
            frappe.throw(_("All fields are required"))
        
        paid_amount = flt(paid_amount)
        if paid_amount <= 0:
            frappe.throw(_("Paid amount must be greater than zero"))
        
        repayment_date = getdate(date)
        if repayment_date > getdate(nowdate()):
            frappe.throw(_("Repayment date cannot be in the future"))
        
        loan_dict = frappe.db.get_value(
            'Loan', 
            parent_doc, 
            ['name', 'applicant', 'loan_product', 'rate_of_interest', 'status', 'docstatus',"loan_amount", 
             "total_payment"], 
            as_dict=True
        )
        
        if not loan_dict:
            frappe.throw(_("Loan document {0} not found").format(parent_doc))
        
        if loan_dict.docstatus != 1:
            frappe.throw(_("Cannot create repayment for non-submitted loan"))
        
        if loan_dict.status in {'Closed', 'Cancelled'}:
            frappe.throw(_("Cannot create repayment for {0} loan").format(loan_dict.status.lower()))
        
        account_details = frappe.db.get_value(
            'Account',
            {
                "name": repayment_account,
                "disabled": 0,
                "is_group": 0,
                "account_type":["IN", ["Bank", "Cash"]]
            }, 
            as_dict=True
        )
        
        if not account_details:
            frappe.throw(_("Account {0} not found").format(repayment_account))
        
        
        if not frappe.has_permission("Loan", "create"):
            frappe.throw(_("Insufficient permissions to create loan repayment"))
        
        repayment_doc = frappe.get_doc({
            'doctype': 'Loan Repayment',
            'against_loan': loan_dict.name,
            'repay_from_salary': 0,
            'amount_paid': paid_amount,
            'posting_date': repayment_date,
            'payment_account': repayment_account,
            'applicant_type': 'Employee',
            'is_additional_repayment': 1
        })
        
        repayment_doc.flags.ignore_permissions = True
        repayment_doc.flags.ignore_mandatory = True
        
        repayment_doc.insert()
        repayment_doc.submit()
        
        update_loan_outstanding_amount(loan_dict)
        update_loan_repayment_schedule(loan_dict)
        
        frappe.db.commit()
        
        return {
            "status": "success",
            "message": _("Additional repayment of {0} created successfully").format(
                frappe.format(paid_amount, {"fieldtype": "Currency"})
            ),
            "repayment_doc": repayment_doc.name,
            "repayment_amount": paid_amount
        }
        
    except Exception as e:
        frappe.db.rollback()
        error_msg = str(e)
        frappe.log_error(
            message=f"Error creating additional repayment for loan {parent_doc}: {error_msg}",
            title="Additional Repayment Creation Error"
        )
        frappe.throw(_("Error creating additional repayment: {0}").format(error_msg))


def update_loan_outstanding_amount(loan_dict):
    try:
        total_repaid = frappe.db.sql("""
            SELECT SUM(amount_paid) as total
            FROM `tabLoan Repayment`
            WHERE against_loan = %s 
            AND applicant = %s
            AND docstatus = 1
            AND amount_paid > 0
        """, (loan_dict.name, loan_dict.applicant))[0][0] or 0
        
        frappe.db.sql("""
            UPDATE `tabLoan`
            SET total_amount_paid = %s,
                total_principal_paid = %s
            WHERE name = %s
        """, (flt(total_repaid), flt(total_repaid), loan_dict.name))
        
        if flt(total_repaid) >= flt(loan_dict.total_payment):
            frappe.db.set_value("Loan", loan_dict.name, "status", "Closed")
            
    except Exception as e:
        frappe.log_error(
            message=f"Error updating loan outstanding amount: {str(e)}",
            title="Loan Outstanding Update Error"
        )



def update_loan_repayment_schedule(loan_dict):
    try:
        total_additional_payments = frappe.db.sql("""
            SELECT SUM(amount_paid) as total
            FROM `tabLoan Repayment`
            WHERE against_loan = %s 
            AND docstatus = 1
            AND repay_from_salary = 0
            AND amount_paid > 0
        """, (loan_dict.name,))[0][0] or 0
        
        if total_additional_payments <= 0:
            return
        
        loan_repayment_schedule_doc = frappe.db.get_value("Loan Repayment Schedule", {"loan": loan_dict.name}, "name")
        if not loan_repayment_schedule_doc:
            return
        
        current_schedules = frappe.db.sql("""
            SELECT name, payment_date, number_of_days, total_payment, principal_amount, 
                   interest_amount, balance_loan_amount, is_accrued, idx,
                   IFNULL(custom_amount_paid_via_additional_payment, 0) as current_additional
            FROM `tabRepayment Schedule`
            WHERE parent = %s
            ORDER BY idx ASC
        """, (loan_repayment_schedule_doc,), as_dict=True)
        
        if not current_schedules:
            return

        remaining_payment = flt(total_additional_payments)

        for i in range(len(current_schedules) - 1, -1, -1):
            schedule = current_schedules[i]
            
            original_total = flt(schedule.total_payment)
            custom_payment = 0
            
            if remaining_payment <= 0:
                custom_payment = 0
            elif remaining_payment >= original_total:
                custom_payment = original_total
                remaining_payment -= original_total
            else:
                custom_payment = remaining_payment
                remaining_payment = 0
            
            frappe.db.sql("""
                UPDATE `tabRepayment Schedule`
                SET custom_amount_paid_via_additional_payment = %s
                WHERE name = %s
            """, (custom_payment, schedule.name))
        
    except Exception as e:
        frappe.log_error(
            message=f"Error updating loan repayment schedule: {str(e)}",
            title="Loan Repayment Schedule Update Error"
        )