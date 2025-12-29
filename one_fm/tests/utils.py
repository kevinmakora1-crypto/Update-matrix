import frappe
from frappe.utils import add_days, nowdate
from frappe.core.doctype.user_permission.test_user_permission import create_user
import erpnext

def get_test_employee():
    """Get or create test employee"""
    if not frappe.db.exists("Employee", {"user_id": "test_employee@example.com"}):
        return make_employee("test_employee@example.com", company="_Test Company")
    return frappe.get_doc("Employee", {"user_id": "test_employee@example.com"})

def make_employee(user, company=None, **kwargs):
    if not frappe.db.get_value("User", user):
        frappe.get_doc(
            {
                "doctype": "User",
                "email": user,
                "first_name": user,
                "new_password": "password",
                "send_welcome_email": 0,
                "roles": [{"doctype": "Has Role", "role": "Employee"}],
            }
        ).insert()

    if not frappe.db.get_value("Employee", {"user_id": user}):
        employee = frappe.get_doc(
            {
                "doctype": "Employee",
                "naming_series": "EMP-",
                "name": "_T-Employee-00001",
                "first_name": user,
                "company": company or erpnext.get_default_company(),
                "user_id": user,
                "date_of_birth": "1990-05-08",
                "date_of_joining": "2013-01-01",
                "department": frappe.get_all("Department", fields="name")[0].name,
                "gender": "Female",
                "company_email": user,
                "prefered_contact_email": "Company Email",
                "prefered_email": user,
                "status": "Active",
                "employment_type": "Intern",
                "last_name": "Test",
                "one_fm_first_name_in_arabic": "اختبار",
                "one_fm_last_name_in_arabic": "الموظف",
                "one_fm_basic_salary": 1000
            }
        )
        if kwargs:
            employee.update(kwargs)
        employee.insert()
        return employee
    else:
        employee = frappe.get_doc("Employee", {"user_id": user})
        employee.update(kwargs)
        employee.status = "Active"
        employee.save()
        return employee


def get_test_leave_type(**kwargs):
    """Create test leave type"""
    leave_type_name = kwargs.get("leave_type_name", "_Test Leave Type")
    if frappe.db.exists("Leave Type", leave_type_name):
        frappe.delete_doc("Leave Type", leave_type_name, force=True)
    
    defaults = {
        "is_lwp": False,
        "include_holiday": False,
        "max_leaves_allowed": 30,
        "is_carry_forward": False,
        "one_fm_is_paid_sick_leave": False,
        "one_fm_is_hajj_leave": False,
        "one_fm_is_paid_annual_leave": False,
        "custom_is_maternity": False,
        "custom_update_employee_status_to_vacation": False,
        "is_proof_document_required": False,
        "allow_negative": False,
        "is_compensatory": False,
        "allow_over_allocation": False,
        "applicable_after": 0,
        "max_continuous_days_allowed": 0,
    }

    defaults.update(kwargs)

    leave_type = frappe.get_doc({
        "doctype": "Leave Type",
        "leave_type_name": leave_type_name,
        "company": "_Test Company",
        **defaults
    })
    leave_type.insert()
    return leave_type

def create_test_leave_allocation(employee, leave_type, **kwargs):
    """Create test leave allocation"""
    from hrms.hr.doctype.leave_allocation.leave_allocation import LeaveAllocation

    allocation_defaults = {
        "doctype": "Leave Allocation",
        "employee": employee.name,
        "leave_type": leave_type.name,
        "from_date": nowdate(),
        "to_date": add_days(nowdate(), 365),
        "new_leaves_allocated": 20,
        "company": "_Test Company",
    }

    allocation_defaults.update(kwargs)

    leave_allocation = LeaveAllocation(allocation_defaults)
    leave_allocation.insert()
    leave_allocation.submit()
    return leave_allocation

def create_test_company():
    # Ensure test company and a default holiday list exist
    if not frappe.db.exists("Holiday List", "_Test Holiday List"):
        frappe.get_doc({
            "doctype": "Holiday List",
            "holiday_list_name": "_Test Holiday List",
        }).insert()

    if not frappe.db.exists("Company", "_Test Company"):
        company = frappe.get_doc({
            "doctype": "Company",
            "company_name": "_Test Company",
            "abbr": "_TC",
            "default_currency": "KWD",
            "country": "Kuwait",
            "default_language": "en",
            "default_holiday_list": "_Test Holiday List"
        })
        company.insert(ignore_permissions=True)
    else:
        # Ensure existing test company has a holiday list
        frappe.db.set_value("Company", "_Test Company", "default_holiday_list", "_Test Holiday List")

def make_leave_application(employee, from_date, to_date, leave_type, company=None, half_day=False, half_day_date=None, submit=False):
    create_user("test@example.com")

    leave_application = frappe.get_doc(
        dict(
            doctype="Leave Application",
            employee=employee,
            leave_type=leave_type,
            from_date=from_date,
            to_date=to_date,
            half_day=half_day,
            half_day_date=half_day_date,
            company=company or erpnext.get_default_company() or "_Test Company",
            status="Open",
            leave_approver="test@example.com",
            resumption_date=add_days(to_date, 1)
        )
    ).insert()

    if submit:
        leave_application.submit()

    return leave_application