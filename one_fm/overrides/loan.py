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
            ['name', 'applicant', 'loan_product', 'rate_of_interest', 'status', 'docstatus',"loan_amount"], 
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
        
        if flt(total_repaid) >= flt(loan_dict.loan_amount):
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

        
        loan_amount = loan_dict.loan_amount - total_additional_payments
        
        original_schedules = []
        for schedule in current_schedules:
            current_total = flt(schedule.total_payment)
            current_additional = flt(schedule.current_additional)
            
            original_total = current_total + current_additional
            
            if original_total > 0 and current_total > 0:
                ratio = current_total / original_total
                original_principal = flt(schedule.principal_amount) / ratio if ratio > 0 else flt(schedule.principal_amount)
                original_interest = flt(schedule.interest_amount) / ratio if ratio > 0 else flt(schedule.interest_amount)
            elif current_additional > 0:
                original_principal = current_additional * 0.8
                original_interest = current_additional * 0.2
                original_total = current_additional
            else:
                original_principal = flt(schedule.principal_amount)
                original_interest = flt(schedule.interest_amount)
                original_total = current_total
            
            original_schedules.append({
                'payment_date': schedule.payment_date,
                'number_of_days': schedule.number_of_days,
                'original_total': original_total,
                'original_principal': original_principal,
                'original_interest': original_interest,
                'is_accrued': schedule.is_accrued,
                'idx': schedule.idx
            })
        
        remaining_payment = flt(total_additional_payments)
        new_schedule_data = []
        
        for i in range(len(original_schedules) - 1, -1, -1):
            schedule = original_schedules[i]
            
            original_total = schedule['original_total']
            original_principal = schedule['original_principal']
            original_interest = schedule['original_interest']
            
            if remaining_payment <= 0:
                new_schedule_data.append({
                    'payment_date': schedule['payment_date'],
                    'number_of_days': schedule['number_of_days'],
                    'total_payment': original_total,
                    'principal_amount': original_principal,
                    'interest_amount': original_interest,
                    'is_accrued': schedule['is_accrued'],
                    'idx': schedule['idx'],
                    'custom_amount_paid_via_additional_payment': 0
                })
            elif remaining_payment >= original_total:
                new_schedule_data.append({
                    'payment_date': schedule['payment_date'],
                    'number_of_days': schedule['number_of_days'],
                    'total_payment': 0,
                    'principal_amount': 0,
                    'interest_amount': 0,
                    'is_accrued': schedule['is_accrued'],
                    'idx': schedule['idx'],
                    'custom_amount_paid_via_additional_payment': original_total
                })
                remaining_payment -= original_total
            else:
                payment_applied = remaining_payment
                amount_still_owed = original_total - payment_applied
                
                ratio = amount_still_owed / original_total
                new_principal = original_principal * ratio
                new_interest = original_interest * ratio
                new_total = new_principal + new_interest
                
                new_schedule_data.append({
                    'payment_date': schedule['payment_date'],
                    'number_of_days': schedule['number_of_days'],
                    'total_payment': new_total,
                    'principal_amount': new_principal,
                    'interest_amount': new_interest,
                    'is_accrued': schedule['is_accrued'],
                    'idx': schedule['idx'],
                    'custom_amount_paid_via_additional_payment': payment_applied
                })
                remaining_payment = 0
        
        new_schedule_data.sort(key=lambda x: x['idx'])
        
        current_balance = flt(loan_amount)
        for data in new_schedule_data:
            current_balance -= flt(data['principal_amount'])
            data['balance_loan_amount'] = max(0, current_balance)
        
        frappe.db.sql("DELETE FROM `tabRepayment Schedule` WHERE parent = %s", (loan_repayment_schedule_doc,))
        
        for data in new_schedule_data:
            frappe.db.sql("""
                INSERT INTO `tabRepayment Schedule`
                (name, parent, parenttype, parentfield, payment_date, number_of_days,
                 total_payment, principal_amount, interest_amount, balance_loan_amount,
                 is_accrued, idx, custom_amount_paid_via_additional_payment)
                VALUES (%(name)s, %(parent)s, 'Loan Repayment Schedule', 'repayment_schedule',
                        %(payment_date)s, %(number_of_days)s, %(total_payment)s,
                        %(principal_amount)s, %(interest_amount)s, %(balance_loan_amount)s,
                        %(is_accrued)s, %(idx)s, %(custom_amount_paid_via_additional_payment)s)
            """, {
                'name': frappe.generate_hash(length=10),
                'parent': loan_repayment_schedule_doc,
                'payment_date': data['payment_date'],
                'number_of_days': data['number_of_days'],
                'total_payment': data['total_payment'],
                'principal_amount': data['principal_amount'],
                'interest_amount': data['interest_amount'],
                'balance_loan_amount': data['balance_loan_amount'],
                'is_accrued': data['is_accrued'],
                'idx': data['idx'],
                'custom_amount_paid_via_additional_payment': data['custom_amount_paid_via_additional_payment']
            })
        
    except Exception as e:
        frappe.log_error(
            message=f"Error updating loan repayment schedule: {str(e)}",
            title="Loan Repayment Schedule Update Error"
        )