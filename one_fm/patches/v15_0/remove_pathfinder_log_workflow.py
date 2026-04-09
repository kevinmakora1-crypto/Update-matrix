import frappe
from frappe.utils import create_batch


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
	delete_pathfinder_log_workflow()


def migrate_workflow_state_to_status():
	"""Map existing workflow_state values to the new status field."""

	if not frappe.db.has_column("Pathfinder Log", "workflow_state"):
		return

	records = frappe.get_all(
		"Pathfinder Log",
		filters={"workflow_state": ["is", "set"]},
		fields=["name", "workflow_state"],
	)

	for batch in create_batch(records, 100):
		for record in batch:
			new_status = WORKFLOW_STATE_TO_STATUS.get(record.workflow_state, "Backlog")
			frappe.db.set_value("Pathfinder Log", record.name, "status", new_status)
		frappe.db.commit()


def delete_pathfinder_log_workflow():
	"""Delete the Pathfinder Log Workflow document if it exists."""

	if frappe.db.exists("Workflow", "Pathfinder Log"):
		frappe.delete_doc("Workflow", "Pathfinder Log", ignore_permissions=True)
