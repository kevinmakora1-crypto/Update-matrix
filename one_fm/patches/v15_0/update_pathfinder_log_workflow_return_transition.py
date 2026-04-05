import frappe
from one_fm.custom.workflow.workflow import get_workflow_json_file, create_workflow


def execute():
	"""Add 'Return' transition to Pathfinder Log workflow (Pending Review → Pending Process Definition)."""
	create_workflow(get_workflow_json_file("pathfinder_log.json"))
	frappe.db.commit()
