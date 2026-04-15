# -*- coding: utf-8 -*-
# Copyright (c) 2026, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ArrivalandDeployment(Document):
    def validate(self):
        self.update_tracker_status()

    def update_tracker_status(self):
        """Sync status back to the Candidate Country Process tracker row (non-recursive)."""
        if not self.candidate_country_process:
            return
        rows = frappe.get_all(
            "Candidate Country Process Details",
            filters={"parent": self.candidate_country_process, "process_name": "Arrival & Deployment"},
            fields=["name"],
            limit=1,
        )
        if not rows:
            return

        updates = {"status": self.status}
        if self.status == "Completed" and self.deployment_date:
            updates["actual_date"] = self.deployment_date
        elif self.arrival_date:
            updates["actual_date"] = self.arrival_date

        for field, value in updates.items():
            frappe.db.set_value("Candidate Country Process Details", rows[0].name, field, value, update_modified=False)
