import frappe
from frappe import _

@frappe.whitelist(methods=["POST"])
def get_stock_entries(stock_entry_type: str = None, from_date: str = None, to_date: str = None):
	"""
	Fetch Stock Entry records with optional filtering.
	"""
	filters = {
		"docstatus": ["!=", 2]  # Exclude cancelled records
	}

	if stock_entry_type and stock_entry_type != "undefined":
		# Handle JSON string or comma-separated string
		if isinstance(stock_entry_type, str):
			if stock_entry_type.startswith("["):
				try:
					import json
					stock_entry_type = json.loads(stock_entry_type)
				except Exception:
					pass
			elif "," in stock_entry_type:
				stock_entry_type = stock_entry_type.split(",")

		if isinstance(stock_entry_type, (list, tuple)):
			# Validate all types in list
			valid_types = [t for t in stock_entry_type if t in ["Material Transfer", "Material Issue"]]
			if valid_types:
				filters["stock_entry_type"] = ["in", valid_types]
		else:
			if stock_entry_type not in ["Material Transfer", "Material Issue"]:
				frappe.throw(_("Invalid Stock Entry Type: {0}").format(stock_entry_type))
			filters["stock_entry_type"] = stock_entry_type
	else:
		# If no type is provided, still restrict to these two as per requirements
		filters["stock_entry_type"] = ["in", ["Material Transfer", "Material Issue"]]

	if from_date:
		filters["posting_date"] = [">=", from_date]
	
	if to_date:
		if "posting_date" in filters:
			filters["posting_date"] = ["between", [from_date, to_date]]
		else:
			filters["posting_date"] = ["<=", to_date]

	# Use frappe.get_list to automatically apply permission checks
	stock_entries = frappe.get_list(
		"Stock Entry",
		filters=filters,
		fields=["name", "stock_entry_type", "from_warehouse", "to_warehouse", "posting_date", "docstatus"],
		order_by="posting_date desc, name desc",
		limit=200
	)

	return stock_entries
