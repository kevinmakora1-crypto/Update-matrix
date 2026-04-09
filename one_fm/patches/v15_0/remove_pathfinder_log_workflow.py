import frappe
from frappe.utils import create_batch

from one_fm.custom.assignment_rule.assignment_rule import (
	get_assignment_rule_json_file, create_assignment_rule,
)


# Mapping from old workflow states to new status values
WORKFLOW_STATE_TO_STATUS = {
	"Draft": "Backlog",
	"Pending Process Classification": "Backlog",
	"Pending Process Definition": "Backlog",
	"Pending Review": "Backlog",
	"Pending Story Definition": "Backlog",
	"In Development": "Active",
	"In Staging": "Active",
	"In Production": "Active",
	"Completed": "Deployed",
}


def execute():
	"""Remove Pathfinder Log workflow and migrate workflow_state to status field."""

	migrate_workflow_state_to_status()
	migrate_time_log_states()
	update_assignment_rules()
	delete_pathfinder_log_workflow()



def migrate_workflow_state_to_status():
	"""Map existing workflow_state values to the new status field."""

	if not frappe.db.has_column("Pathfinder Log", "workflow_state"):
		return

	if not frappe.db.has_column("Pathfinder Log", "status"):
		return

	records = frappe.get_all(
		"Pathfinder Log",
		filters={"workflow_state": ["is", "set"]},
		fields=["name", "workflow_state"],
	)

	for batch in create_batch(records, 100):
		for record in batch:
			new_status = WORKFLOW_STATE_TO_STATUS.get(record.workflow_state, "Backlog")
			frappe.db.set_value(
				"Pathfinder Log", record.name, "status", new_status,
				update_modified=False,
			)
		frappe.db.commit()


def migrate_time_log_states():
	"""Migrate Pathfinder Log Time.state from old workflow state strings to new status values."""

	if not frappe.db.has_column("Pathfinder Log Time", "state"):
		return

	records = frappe.get_all(
		"Pathfinder Log Time",
		filters={"state": ["in", list(WORKFLOW_STATE_TO_STATUS.keys())]},
		fields=["name", "state"],
	)

	for batch in create_batch(records, 100):
		for record in batch:
			new_state = WORKFLOW_STATE_TO_STATUS.get(record.state, record.state)
			frappe.db.set_value(
				"Pathfinder Log Time", record.name, "state", new_state,
				update_modified=False,
			)
		frappe.db.commit()


def update_assignment_rules():
	"""Re-apply Pathfinder Log assignment rules with updated status-based conditions."""

	create_assignment_rule(get_assignment_rule_json_file("pathfinder_log_business_analyst.json"))
	create_assignment_rule(get_assignment_rule_json_file("pathfinder_log_process_owner.json"))


def delete_pathfinder_log_workflow():
	"""Delete the Pathfinder Log Workflow document if it exists."""

	if frappe.db.exists("Workflow", "Pathfinder Log"):
		frappe.delete_doc("Workflow", "Pathfinder Log", ignore_permissions=True)
