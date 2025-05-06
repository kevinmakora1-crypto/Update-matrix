# Copyright (c) 2025, omar jaber and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeMonthlyAction(Document):
    def on_submit(self):
        for row in self.goal_update:
            goal_doc = frappe.get_value("Goal", {"goal_name": row.goal}, "name")
            if goal_doc and row.current_progress:
                frappe.db.set_value("Goal", goal_doc, "progress", row.current_progress)
