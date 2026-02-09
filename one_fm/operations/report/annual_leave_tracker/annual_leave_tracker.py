# Copyright (c) 2024, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, flt

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"label": _("Employee ID"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120
		},
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Designation"),
			"fieldname": "designation",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": _("Project"),
			"fieldname": "project",
			"fieldtype": "Link",
			"options": "Project",
			"width": 140
		},
		{
			"label": _("Leave Application"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Leave Application",
			"width": 150
		},
		{
			"label": _("Leave Start Date"),
			"fieldname": "from_date",
			"fieldtype": "Date",
			"width": 110
		},
		{
			"label": _("Leave End Date"),
			"fieldname": "to_date",
			"fieldtype": "Date",
			"width": 110
		},
		{
			"label": _("Leave Approved?"),
			"fieldname": "workflow_state",
			"fieldtype": "Data",
			"width": 130
		},
		{
			"label": _("Reliever ID"),
			"fieldname": "reliever_id",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120
		},
		{
			"label": _("Reliever Name"),
			"fieldname": "reliever_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Reports To"),
			"fieldname": "reports_to",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": _("Site Supervisor"),
			"fieldname": "site_supervisor",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": _("Coverage Readiness"),
			"fieldname": "coverage_readiness",
			"fieldtype": "Data",
			"width": 160
		},
		{
			"label": _("Return Ticket Submitted"),
			"fieldname": "return_ticket_submitted",
			"fieldtype": "Data", # Select displayed as Data
			"width": 160
		},
		{
			"label": _("Actual Return Date"),
			"fieldname": "actual_return_date",
			"fieldtype": "Date",
			"width": 140
		},
		{
			"label": _("Last Update Date"),
			"fieldname": "modified",
			"fieldtype": "Date",
			"width": 140
		},
		{
			"label": _("Final Status"),
			"fieldname": "final_status",
			"fieldtype": "Data",
			"width": 160
		}
	]

def get_data(filters):
	data = []
	conditions, values = get_conditions(filters)
	
	# Fetch Leave Applications
	query = f"""
		SELECT
			la.name, la.employee, la.employee_name, la.from_date, la.to_date, 
			la.status, la.workflow_state, la.modified,
			la.custom_reliever_ as reliever_id, la.custom_reliever_name as reliever_name,
			la.return_ticket_submitted, la.actual_return_date,
			emp.designation, emp.project, emp.reports_to, emp.status as employee_status,
            emp.site as employee_site
		FROM
			`tabLeave Application` la
		LEFT JOIN
			`tabEmployee` emp ON la.employee = emp.name
		WHERE
			la.leave_type = 'Annual Leave'
			and la.docstatus != 2
			{conditions}
		ORDER BY la.from_date DESC
	"""
	
	leaves = frappe.db.sql(query, values, as_dict=1)

	for leave in leaves:
		row = leave.copy()
		
		# Fetch details for Reports To and Site Supervisor names if needed
		if row.get("reports_to"):
			row["reports_to"] = frappe.get_value("Employee", row["reports_to"], "employee_name")

		# Site Supervisor
		if row.get("employee_site"):
			site_supervisor = frappe.db.get_value("Operations Site", row["employee_site"], "site_supervisor")
			if site_supervisor:
				row["site_supervisor"] = frappe.get_value("Employee", site_supervisor, "employee_name")
		
		# Logic for Coverage Readiness
		coverage_readiness = ""
		is_approved = (row.get("status") == "Approved") or (row.get("workflow_state") == "Approved")
		has_reliever = bool(row.get("reliever_id"))
		
		if is_approved and has_reliever:
			coverage_readiness = "OK"
		elif not has_reliever:
			if not is_approved:
				coverage_readiness = "Pending"
			else:
				coverage_readiness = "Shortage"
		else:
			coverage_readiness = "Pending"

		row["coverage_readiness"] = coverage_readiness


		# Logic for Final Status
		current_date = getdate(nowdate())
		start_date = getdate(row.get("from_date"))
		end_date = getdate(row.get("to_date"))
		emp_status = row.get("employee_status")
		
		final_status = ""
		
		if row.get("status") == "Cancelled" or row.get("workflow_state") == "Cancelled":
			final_status = "Cancelled"
		
		elif emp_status == "Not Returned from Leave":
			final_status = "Not Returned From Leave"
		
		elif emp_status in ["Absconding", "Left"]:
			final_status = emp_status

		elif start_date > current_date:
			final_status = row.get("workflow_state")
			
		elif start_date <= current_date:
			final_status = emp_status
			
		row["final_status"] = final_status
		
		# Apply Filters for Coverage Readiness if selected
		if filters.get("coverage_readiness"):
			if filters["coverage_readiness"] != row["coverage_readiness"]:
				continue
				
		data.append(row)
		
	return data

def get_conditions(filters):
	conditions = ""
	values = {}
	
	if filters.get("employee"):
		conditions += " AND la.employee = %(employee)s"
		values["employee"] = filters.get("employee")
		
	if filters.get("department"):
		conditions += " AND emp.department = %(department)s"
		values["department"] = filters.get("department")
		
	if filters.get("project"):
		conditions += " AND emp.project = %(project)s"
		values["project"] = filters.get("project")
		
	if filters.get("from_date"):
		conditions += " AND la.from_date >= %(from_date)s"
		values["from_date"] = filters.get("from_date")
		
	if filters.get("to_date"):
		conditions += " AND la.to_date <= %(to_date)s"
		values["to_date"] = filters.get("to_date")
		
	return conditions, values
