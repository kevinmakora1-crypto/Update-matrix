# Copyright (c) 2026, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe import _


@frappe.whitelist()
def is_process_editable(process_name: str) -> dict:
	"""
	Check if a process has an active (non-Completed) Pathfinder Log.

	Called by the BA site to determine whether the Processa editor
	should allow editing for a given process.

	A process is editable only if there is at least one Pathfinder Log
	linked to it whose workflow_state is NOT 'Completed'.

	Args:
		process_name: The name of the Process record.

	Returns:
		dict with:
			- editable (bool): True if an active Pathfinder Log exists
			- pathfinder_log (str|None): Name of the most recent active log
			- workflow_state (str|None): Current workflow state of that log
	"""
	if not process_name:
		frappe.throw(_("Process name is required"))

	# Find the most recent non-Completed Pathfinder Log for this process
	active_log = frappe.db.get_value(
		"Pathfinder Log",
		filters={
			"process_name": process_name,
			"workflow_state": ["!=", "Completed"],
		},
		fieldname=["name", "workflow_state"],
		order_by="modified desc",
		as_dict=True,
	)

	if active_log:
		return {
			"editable": True,
			"pathfinder_log": active_log.name,
			"workflow_state": active_log.workflow_state,
		}

	return {
		"editable": False,
		"pathfinder_log": None,
		"workflow_state": None,
	}


@frappe.whitelist()
def bulk_check_process_editable(process_names: str) -> dict:
	"""
	Batch check editability for multiple processes in a single call.

	Args:
		process_names: JSON-encoded list of process name strings.

	Returns:
		dict mapping each process name to its editability status.
	"""
	import json

	if isinstance(process_names, str):
		process_names = json.loads(process_names)

	if not isinstance(process_names, list):
		frappe.throw(_("process_names must be a list"))

	result = {}
	for pname in process_names:
		active_log = frappe.db.get_value(
			"Pathfinder Log",
			filters={
				"process_name": pname,
				"workflow_state": ["!=", "Completed"],
			},
			fieldname=["name", "workflow_state"],
			order_by="modified desc",
			as_dict=True,
		)
		if active_log:
			result[pname] = {
				"editable": True,
				"pathfinder_log": active_log.name,
				"workflow_state": active_log.workflow_state,
			}
		else:
			result[pname] = {
				"editable": False,
				"pathfinder_log": None,
				"workflow_state": None,
			}

	return result
