import frappe
from one_fm.api.v1.utils import response
from frappe.utils import getdate, add_months
from one_fm.utils import (
    get_approver
)
from one_fm.api.notification import get_employee_user_id
from frappe.model.workflow import apply_workflow

@frappe.whitelist()
def shift_request_list(employee_id: str, from_date: str = None, to_date: str = None, 
                       purpose: str = None, status: str = None) -> dict:
    """
    Retrives list of shift requests for both employee and reports to.
    Reports to is based on custom_reports_to field in Shift Request.
    """
    try:
        if not employee_id:
            return response("error", 400, {}, "Employee ID is required.")
            
        employee = frappe.get_value("Employee", {"employee_id": employee_id}, ["name", "user_id"], as_dict=1)
        if not employee:
            return response("error", 404, {}, "No employee record found for {employee_id}".format(employee_id=employee_id))
        
        # Default date range if not provided (last 12 months)
        if not (from_date and to_date):
            from_date = add_months(getdate(), -12)
            to_date = getdate()
            
        base_filters = {
            "from_date": ["between", [from_date, to_date]],
            "to_date": ["between", [from_date, to_date]],
            "purpose": ["in", ["Assign Day Off", "Day Off Overtime"]]
        }
        if purpose:
            base_filters["purpose"] = purpose
        if status:
            base_filters["workflow_state"] = status
            
        # My Shifts
        my_shifts_query = frappe.get_list("Shift Request", 
            filters={**base_filters, "employee": employee.name},
            fields=["name", "employee_name", "workflow_state", "purpose", "from_date", "to_date", "reason"]
        )
        
        # Reports To - Fetching requests where custom_reports_to is the current employee
        reports_to_query = frappe.get_list("Shift Request", 
            filters={**base_filters, "custom_project_manager": employee.name},
            fields=["name", "employee_name", "workflow_state", "purpose", "from_date", "to_date", "reason"]
        )
        
        return response("success", 200, {"my_shifts": my_shifts_query, "reports_to": reports_to_query})
        
    except Exception as e:
        frappe.log_error(title="Shift Request List API", message=frappe.get_traceback())
        return response("error", 500, {}, str(e))

@frappe.whitelist()
def get_shift_request_detail(shift_request_id: str) -> dict:
    """
    Returns details of a specific shift request.
    """
    try:
        if not shift_request_id:
            return response("error", 400, {}, "Shift Request ID is required.")
            
        doc = frappe.get_doc("Shift Request", shift_request_id)
        data = doc.as_dict()
        
        # Check if user is the manager (custom_reports_to_user)
        is_approver = 0
        if doc.custom_project_manager_user == frappe.session.user:
            is_approver = 1
                
        data.update({"is_approver": is_approver})
        
        return response("Success", 200, data)
    except Exception as e:
        frappe.log_error(title="Shift Request Detail API", message=frappe.get_traceback())
        return response("error", 500, {}, str(e))

@frappe.whitelist()
def create_shift_request(employee_id: str, purpose: str, from_date: str, to_date: str, reason: str = None) -> dict:
    """
    Creates a new Shift Request.
    """
    try:
        if not all([employee_id, purpose, from_date, to_date]):
            return response("error", 400, {}, "Missing required fields.")
            
        employee = frappe.get_doc("Employee", {"employee_id": employee_id})
        
        shift_req = frappe.new_doc("Shift Request")
        shift_req.employee = employee.name
        if not reason:
            shift_req.reason = "Shift Request Application for {purpose} from {employee_name}".format(purpose=purpose, employee_name=employee.employee_name)
        else:
            shift_req.reason = reason
        shift_req.purpose = purpose
        shift_req.from_date = from_date
        shift_req.to_date = to_date
        shift_req.company = employee.company
        shift_req.department = employee.department
        
        # Set defaults from employee
        shift_req.shift_type = employee.default_shift
        shift_req.site = employee.site
        shift_req.project = employee.project
        shift_req.operations_role = employee.custom_operations_role_allocation
        shift_req.operations_shift = employee.shift
        
        # Reports to logic
        approver = get_approver(employee.name)
        approver_user_id = get_employee_user_id(approver)
        shift_req.approver = approver_user_id
        shift_req.insert()
        shift_req.db_set('workflow_state',"Pending Approval")
        frappe.db.commit()
        
        return response("Success", 201, shift_req.as_dict())
    except Exception as e:
        frappe.log_error(title="Create Shift Request API", message=frappe.get_traceback())
        return response("error", 500, {}, str(e))

@frappe.whitelist()
def shift_request_action(shift_request_id: str, action: str, reason: str = None) -> dict:
    """
    Performs a workflow action (e.g., Approve, Reject) on a shift request.
    """
    current_user = frappe.session.user
    try:
        doc = frappe.get_doc("Shift Request", shift_request_id)
        
        # Permission check: current user must be the manager
        if doc.custom_project_manager_user != frappe.session.user and frappe.session.user != "Administrator":
             return response("error", 403, {}, "You are not authorized to perform this action.")

        if reason:
            doc.db_set('reason', reason)

        # Apply workflow action
        
        apply_workflow(doc, action)
        

        return response("Success", 200, doc.as_dict())
    except Exception as e:
        frappe.log_error(title="Shift Request Action API", message=frappe.get_traceback())
        return response("error", 500, {}, str(e))
