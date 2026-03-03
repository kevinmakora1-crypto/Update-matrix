import frappe

DELETED_ASSIGNMENT_RULES = [
	"Attendance Check Site Supervisor",
	"Attendance Check Reports To",
	"Attendance Check Shift Supervisor",
]

def execute():
	"""
	Clean up orphaned ToDo records that still reference Assignment Rules
	which were deleted by the patch `add_assignment_rule_action_attendance_check_approver`.

	When Frappe closes a ToDo during workflow approval, it runs link validation
	which throws a LinkValidationError because the referenced Assignment Rule no
	longer exists. This prevents bulk approval of Attendance Check records.
	"""
	placeholders = ", ".join(["%s"] * len(DELETED_ASSIGNMENT_RULES))
	frappe.db.sql(
		f"""
		UPDATE `tabToDo`
		SET assignment_rule = NULL
		WHERE assignment_rule IN ({placeholders})
		""",
		DELETED_ASSIGNMENT_RULES,
	)
	frappe.db.commit()

	count = frappe.db.sql(
		f"""
		SELECT COUNT(*) FROM `tabToDo`
		WHERE assignment_rule IN ({placeholders})
		""",
		DELETED_ASSIGNMENT_RULES,
	)[0][0]

	if count == 0:
		frappe.logger().info(
			"Patch clean_orphaned_attendance_check_todos: Successfully cleared orphaned ToDo references."
		)
	else:
		frappe.logger().warning(
			f"Patch clean_orphaned_attendance_check_todos: {count} orphaned ToDo records remain after cleanup."
		)
