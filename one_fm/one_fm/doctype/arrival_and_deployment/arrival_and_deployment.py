# -*- coding: utf-8 -*-
# Copyright (c) 2026, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ArrivalandDeployment(Document):
    def validate(self):
        self.update_tracker_status()

    def update_tracker_status(self):
        """Sync status back to the Candidate Country Process tracker row."""
        if not self.candidate_country_process:
            return
        ccp = frappe.get_doc("Candidate Country Process", self.candidate_country_process)
        for row in ccp.agency_process_details:
            if row.process_name == "Arrival & Deployment":
                row.status = self.status
                if self.status == "Completed" and self.deployment_date:
                    row.actual_date = self.deployment_date
                elif self.arrival_date:
                    row.actual_date = self.arrival_date
                break
        ccp.save(ignore_permissions=True)
