# -*- coding: utf-8 -*-
# Copyright (c) 2020, ONE FM and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CandidateCountryProcess(Document):
    def validate(self):
        today = frappe.utils.getdate()
        rows = self.agency_process_details

        # ── 1. PLANNED DATE: static single-pass sequential cascade ────────────
        # Only recalculate if the row has no planned_date yet (first creation).
        # Never overwrite a planned_date that already exists.
        anchor = frappe.utils.getdate(self.start_date) if self.start_date else None
        for row in rows:
            if not row.get("planned_date") and anchor and row.duration_in_days is not None:
                row.planned_date = frappe.utils.add_days(anchor, row.duration_in_days)
            # Advance anchor sequentially (parallel rows share the same anchor;
            # the master template already accounts for this via duration)
            if row.get("planned_date"):
                anchor = frappe.utils.getdate(row.planned_date)

        # ── 2. LIVE PLAN DATE: Fork-Join dynamic cascade ──────────────────────
        # Rules:
        #   • parallel_group == 0  → sequential step
        #   • parallel_group  > 0  → rows sharing the same group id run in
        #     parallel from the same live_anchor
        #   • After a parallel group the live_anchor = MAX(all tracks' end dates)
        live_anchor = frappe.utils.getdate(self.start_date) if self.start_date else None
        i = 0
        while i < len(rows):
            row = rows[i]
            group_id = frappe.utils.cint(row.get("parallel_group") or 0)

            if group_id == 0:
                # ── Sequential step ──────────────────────────────────────────
                if live_anchor and row.duration_in_days is not None:
                    row.live_plan_date = frappe.utils.add_days(live_anchor, row.duration_in_days)

                # Advance live anchor: actual beats live plan
                if row.actual_date:
                    live_anchor = frappe.utils.getdate(row.actual_date)
                elif row.get("live_plan_date"):
                    live_anchor = frappe.utils.getdate(row.live_plan_date)

                i += 1

            else:
                # ── Parallel group: collect all consecutive rows in this group ─
                group_rows = []
                j = i
                while j < len(rows) and frappe.utils.cint(rows[j].get("parallel_group") or 0) == group_id:
                    group_rows.append(rows[j])
                    j += 1

                group_start = live_anchor
                max_end = group_start

                for gr in group_rows:
                    if group_start and gr.duration_in_days is not None:
                        gr.live_plan_date = frappe.utils.add_days(group_start, gr.duration_in_days)

                    # Each track's effective end date
                    if gr.actual_date:
                        track_end = frappe.utils.getdate(gr.actual_date)
                    elif gr.get("live_plan_date"):
                        track_end = frappe.utils.getdate(gr.live_plan_date)
                    else:
                        track_end = group_start

                    if track_end and (max_end is None or track_end > max_end):
                        max_end = track_end

                # After the parallel group, live anchor = latest of all tracks
                live_anchor = max_end
                i = j

        # ── 3. ETA STATUS: based on planned date vs actual / today ───────────
        for row in rows:
            planned = frappe.utils.getdate(row.get("planned_date")) if row.get("planned_date") else None
            actual  = frappe.utils.getdate(row.actual_date) if row.actual_date else None

            if not actual:
                if planned and today > planned:
                    row.eta_status = "Late"
                else:
                    row.eta_status = "Still Within Time frame"
            else:
                if planned and actual > planned:
                    row.eta_status = "Late"
                elif planned and actual < planned:
                    row.eta_status = "Completed Early"
                else:
                    row.eta_status = "Completed on time"

        # ── 4. Mirror Live Plan ETA to header field ───────────────────────────
        if rows:
            last = rows[-1]
            if last.get("live_plan_date"):
                self.live_plan_eta = last.live_plan_date
            elif last.get("planned_date"):
                self.live_plan_eta = last.planned_date

    def autoname(self):
        if not self.candidate_name and self.job_applicant:
            self.candidate_name = frappe.db.get_value('Job Applicant', self.job_applicant, 'applicant_name')

        if self.candidate_name and self.job_offer:
            self.name = f"{self.candidate_name} - {self.job_offer}"
        elif self.candidate_name:
            self.name = self.candidate_name
        else:
            from frappe.model.naming import make_autoname
            self.name = make_autoname('CCP-#####')

    def after_insert(self):
        if self.agency_process_details:
            for agency_process_details in self.agency_process_details:
                if agency_process_details.reference_type:
                    self.current_process_id = agency_process_details.name
                    self.db_set('current_process_id', agency_process_details.name)
                    break

    def on_submit(self):
        pass

    def get_workflow(self):
        workflow_list = []
        if self.agency_process_details:
            for workflow in self.agency_process_details:
                if workflow.reference_type and workflow.name == self.current_process_id:
                    if workflow.reference_name:
                        workflow_list.append(frappe.get_doc(workflow.reference_type, workflow.reference_name).as_dict())
                    else:
                        workflow_list.append({"new_doc": True, "doctype": workflow.reference_type})
        return workflow_list


def update_candidate_country_process():
    query = """
        select
            dt.name as dt_name, ccp.name as ccp_name, dt.process_name, dt.reference_type, dt.reference_name,
            dt.reference_complete_status_value, dt.reference_complete_status_field, dt.idx, dt.planned_date
        from
            `tabCandidate Country Process` ccp, `tabCandidate Country Process Details` dt
        where
            ccp.current_process_id=dt.name
    """
    ccp_list = frappe.db.sql(query, as_dict=True)
    today = frappe.utils.getdate()

    for ccp in ccp_list:
        delay = 0
        if ccp.planned_date and today > ccp.planned_date:
            delay = (today - ccp.planned_date).days

        if ccp.reference_type and ccp.ccp_name:
            process_doc = frappe.get_doc(ccp.reference_type, {'candidate_country_process': ccp.ccp_name})
            if process_doc:
                if not ccp.reference_name:
                    frappe.db.set_value('Candidate Country Process Details', ccp.dt_name, 'reference_name', process_doc.name)

                if process_doc.get(ccp.reference_complete_status_field) == ccp.reference_complete_status_value:
                    frappe.db.set_value('Candidate Country Process Details', ccp.dt_name, 'status', 'Approved')
                    frappe.db.set_value('Candidate Country Process Details', ccp.dt_name, 'actual_date', today)

                    ccp_doc = frappe.get_doc('Candidate Country Process', ccp.ccp_name)

                    if len(ccp_doc.agency_process_details) > ccp.idx:
                        for process_list in ccp_doc.agency_process_details:
                            if process_list.idx > ccp.idx and process_list.reference_type:
                                ccp_doc.db_set('current_process_id', process_list.name)
                                break
                    ccp_doc.save(ignore_permissions=True)
