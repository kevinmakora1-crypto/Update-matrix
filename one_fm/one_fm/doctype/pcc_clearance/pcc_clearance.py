# -*- coding: utf-8 -*-
# Copyright (c) 2026, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PCCClearance(Document):
    def validate(self):
        self.update_tracker_status()

    def update_tracker_status(self):
        """Sync status back to the Candidate Country Process tracker row."""
        if not self.candidate_country_process:
            return
        ccp = frappe.get_doc("Candidate Country Process", self.candidate_country_process)
        for row in ccp.agency_process_details:
            if row.process_name == "PCC Clearance":
                row.status = self.status
                if self.clearance_date:
                    row.actual_date = self.clearance_date
                elif self.application_date and self.status == "Applied":
                    row.actual_date = self.application_date
                break
        ccp.save(ignore_permissions=True)
