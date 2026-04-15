# -*- coding: utf-8 -*-
# Copyright (c) 2026, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OverseasRemedical(Document):
    def validate(self):
        self.update_tracker_status()

    def update_tracker_status(self):
        """Sync status back to the Candidate Country Process tracker row."""
        if not self.candidate_country_process:
            return
        rows = frappe.get_all(
            "Candidate Country Process Details",
            filters={"parent": self.candidate_country_process, "process_name": "Remedical Test"},
            fields=["name"],
            limit=1,
        )
        if not rows:
            return

        updates = {"status": self.status}
        if self.status in ("Fit", "Passed") and self.result_date:
            updates["actual_date"] = self.result_date
        elif self.status == "Skipped":
            updates["actual_date"] = frappe.utils.today()

        for field, value in updates.items():
            frappe.db.set_value(
                "Candidate Country Process Details", rows[0].name,
                field, value, update_modified=False
            )
