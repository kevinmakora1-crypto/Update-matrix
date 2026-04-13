import frappe

def execute(filters=None):
	columns = [
		{"fieldname": "project_request_code", "label": "Project Request Code", "fieldtype": "Data"},
		{"fieldname": "status", "label": "Status", "fieldtype": "Data"},
		{"fieldname": "priority", "label": "Priority", "fieldtype": "Data"},
		{"fieldname": "reason", "label": "Manpower Type", "fieldtype": "Data"},
		{"fieldname": "project", "label": "Project", "fieldtype": "Data"},
		{"fieldname": "designation", "label": "Designation", "fieldtype": "Data"},
		{"fieldname": "nationality", "label": "Nationality", "fieldtype": "Data"},
		{"fieldname": "gender", "label": "Gender", "fieldtype": "Data"},
		{"fieldname": "qty", "label": "Total Qty", "fieldtype": "Int"},
		{"fieldname": "cancelled", "label": "Cancelled", "fieldtype": "Int"},
		{"fieldname": "managed_by_ot", "label": "Managed by OT", "fieldtype": "Int"},
		{"fieldname": "remaining_qty", "label": "Remaining Qty", "fieldtype": "Int"},
		{"fieldname": "erf", "label": "ERF", "fieldtype": "Data"},
		{"fieldname": "number_to_hire", "label": "Number to Hire", "fieldtype": "Int"}
	]

	conditions = ""
	
	def build_condition(field, filter_val, use_like=False):
		if not filter_val: return ""
		if isinstance(filter_val, list):
			cleaned = [frappe.db.escape(str(v)) for v in filter_val]
			return f" AND {field} IN ({','.join(cleaned)})"
		if use_like:
			return f" AND {field} LIKE '%%{frappe.db.escape(str(filter_val))[1:-1]}%%'"
		return f" AND {field} = {frappe.db.escape(str(filter_val))}"

	if filters:
		conditions += build_condition('status', filters.get('status'))
		conditions += build_condition('reason', filters.get('reason'))
		conditions += build_condition('project_request_code', filters.get('project_request_code'), True)
		conditions += build_condition('project_allocation', filters.get('project_allocation'))
		conditions += build_condition('designation', filters.get('designation'), True)
		conditions += build_condition('nationality', filters.get('nationality'), True)
		conditions += build_condition('gender', filters.get('gender'))

	sql_query = f"""
		SELECT
			project_request_code, status, priority, reason, project_allocation AS project,
			designation, nationality, gender, count AS qty, cancelled_qty AS cancelled,
			managed_by_ot_qty AS managed_by_ot, remaining_qty, erf, number_to_hire
		FROM
			`tabProject Manpower Request`
		WHERE
			docstatus < 2 {conditions}
		ORDER BY
			modified DESC
	"""
	
	data = frappe.db.sql(sql_query, as_dict=True)
	
	report_summary = []
	if data:
		total_remaining = sum((row.get("remaining_qty") or 0) for row in data)
		total_to_hire = sum((row.get("number_to_hire") or 0) for row in data)
		
		report_summary = [
			{"value": total_remaining, "indicator": "Blue", "label": "Remaining Qty", "datatype": "Int"},
			{"value": total_to_hire, "indicator": "Green", "label": "Number to Hire", "datatype": "Int"}
		]
	
	# Output the premium Report Summary widgets 
	return columns, data, None, None, report_summary, False
