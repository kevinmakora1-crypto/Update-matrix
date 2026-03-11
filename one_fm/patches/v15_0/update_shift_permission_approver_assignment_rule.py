import frappe
from one_fm.custom.assignment_rule.assignment_rule import get_assignment_rule_json_file, create_assignment_rule


def execute():
	"""
	Update the 'Shift Permission Approver' Assignment Rule to include
	Arrival Time (for log_type IN) or Leaving Time (for log_type OUT)
	in the email notification description, between the Log Type and Reason rows.

	The description uses Jinja ternary expressions ({{ 'X' if cond else 'Y' }})
	which survive Frappe's HTML sanitizer on doc.save(), unlike block tags ({% if %}).
	"""
	create_assignment_rule(get_assignment_rule_json_file("shift_permission_approver.json"))
