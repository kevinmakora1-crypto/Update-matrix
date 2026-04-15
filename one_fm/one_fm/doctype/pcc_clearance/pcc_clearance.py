# -*- coding: utf-8 -*-
# Copyright (c) 2026, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PCCClearance(Document):
    def validate(self):
        self.update_tracker_status()

    def update_tracker_status(self):
        """Sync status back to the Candidate Country Process tracker row (non-recursive)."""
        if not self.candidate_country_process:
            return
        rows = frappe.get_all(
            "Candidate Country Process Details",
            filters={"parent": self.candidate_country_process, "process_name": "PCC Clearance"},
            fields=["name"],
            limit=1,
        )
        if not rows:
            return

        updates = {"status": self.status}
        if self.clearance_date:
            updates["actual_date"] = self.clearance_date
        elif self.application_date and self.status == "Applied":
            updates["actual_date"] = self.application_date

        for field, value in updates.items():
            frappe.db.set_value("Candidate Country Process Details", rows[0].name, field, value, update_modified=False)
