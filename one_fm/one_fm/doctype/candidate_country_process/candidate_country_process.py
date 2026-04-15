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

        # ── 1. PLANNED DATE: static sequential baseline set once at creation ──
        # Only fill in rows that don't yet have a planned_date (first save).
        anchor = frappe.utils.getdate(self.start_date) if self.start_date else None
        for row in rows:
            if not row.get("planned_date") and anchor and row.duration_in_days is not None:
                row.planned_date = frappe.utils.add_days(anchor, row.duration_in_days)
            if row.get("planned_date"):
                anchor = frappe.utils.getdate(row.planned_date)

        # ── 2. LIVE PLAN DATE: Track-based Fork-Join cascade ─────────────────
        #
        # parallel_group == 0  → standard sequential step
        # parallel_group  > 0  → rows sharing the same group id form one TRACK.
        #                         Within a track, rows run sequentially.
        #                         Different group ids run as separate parallel tracks.
        #                         After all tracks finish, the sequential anchor
        #                         advances to MAX(effective end of each track).
        #
        # A row with status == "Skipped" is excluded from the track-end calculation.
        #
        live_anchor = frappe.utils.getdate(self.start_date) if self.start_date else None
        i = 0
        while i < len(rows):
            row = rows[i]
            group_id = frappe.utils.cint(row.get("parallel_group") or 0)

            if group_id == 0:
                # ── Sequential step ──────────────────────────────────────────
                if live_anchor and row.duration_in_days is not None:
                    row.live_plan_date = frappe.utils.add_days(live_anchor, row.duration_in_days)

                if row.actual_date:
                    live_anchor = frappe.utils.getdate(row.actual_date)
                elif row.get("live_plan_date"):
                    live_anchor = frappe.utils.getdate(row.live_plan_date)

                i += 1

            else:
                # ── Collect ALL rows inside the parallel section ─────────────
                # Group consecutive non-zero rows into their respective tracks.
                tracks = {}   # {group_id: [rows…]}
                j = i
                while j < len(rows) and frappe.utils.cint(rows[j].get("parallel_group") or 0) != 0:
                    gid = frappe.utils.cint(rows[j].parallel_group)
                    tracks.setdefault(gid, []).append(rows[j])
                    j += 1

                max_end = live_anchor  # will become the sequential anchor after the fork-join

                for track_rows in tracks.values():
                    track_anchor = live_anchor
                    track_effective_end = live_anchor

                    for tr in track_rows:
                        # Skipped rows don't advance the track anchor
                        if tr.get("status") == "Skipped":
                            tr.live_plan_date = None
                            continue

                        if track_anchor and tr.duration_in_days is not None:
                            tr.live_plan_date = frappe.utils.add_days(track_anchor, tr.duration_in_days)

                        # Advance within the track: actual beats live plan
                        if tr.actual_date:
                            track_anchor = frappe.utils.getdate(tr.actual_date)
                            track_effective_end = track_anchor
                        elif tr.get("live_plan_date"):
                            track_anchor = frappe.utils.getdate(tr.live_plan_date)
                            track_effective_end = track_anchor

                    # Join: take the latest of all track endings
                    if track_effective_end and (max_end is None or track_effective_end > max_end):
                        max_end = track_effective_end

                live_anchor = max_end
                i = j

        # ── 3. ETA STATUS: planned date vs actual / today ────────────────────
        for row in rows:
            if row.get("status") == "Skipped":
                row.eta_status = ""
                continue

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

    def on_update(self):
        """Auto-create linked DocType records when a step reaches its trigger status."""
        if getattr(self.flags, '_in_auto_create', False):
            return
        self.flags._in_auto_create = True
        try:
            self._auto_create_next_records()
        finally:
            self.flags._in_auto_create = False

    def _auto_create_next_records(self):
        """
        Trigger logic: When a process step's status matches its completion value,
        auto-create records for the NEXT step(s) that don't already have a reference_name.

        Example flow:
          Job Offer → "Offer Accepted" → triggers: PAM Visa, Medical, PCC (parallel)
          Medical "Fit" + PCC "Issued" → triggers: Visa Stamping
          Visa Stamping "Approved" → triggers: Arrival & Deployment
        """
        rows = self.agency_process_details
        if not rows:
            return

        # Map of which process triggers which next processes
        # When the trigger process reaches its completion status,
        # create records for all target processes
        TRIGGER_MAP = {
            # Step 1 → Step 2: Job Offer accepted → create PAM Visa
            "Job Offer Issuance": {
                "trigger_status": "Offer Accepted",
                "creates": ["Visa Processing"]
            },
            # Step 2 → Steps 3+5: PAM Visa approved → create Medical + PCC (parallel)
            "Visa Processing": {
                "trigger_status": "Issued",
                "creates": ["Medical Test", "PCC Clearance"]
            },
            # Parallel tracks: no direct creates, fork-join handles Visa Stamping
            "Medical Test": {
                "trigger_status": "Fit",
                "creates": []
            },
            "Remedical Test": {
                "trigger_status": "Fit",
                "creates": []
            },
            "PCC Clearance": {
                "trigger_status": "Issued",
                "creates": []
            },
            # Step 6 → Step 7: Visa Stamping approved → create Arrival & Deployment
            "Visa Stamping": {
                "trigger_status": "Approved",
                "creates": ["Arrival & Deployment"]
            },
        }

        # Check each row for triggers
        for row in rows:
            trigger = TRIGGER_MAP.get(row.process_name)
            if not trigger:
                continue

            if row.status != trigger["trigger_status"]:
                continue

            # This step is complete — create records for target processes
            for target_process in trigger["creates"]:
                target_row = next((r for r in rows if r.process_name == target_process), None)
                if not target_row or not target_row.reference_type:
                    continue

                # Skip if record already exists
                if target_row.reference_name:
                    continue

                new_doc = self._create_linked_record(target_row)
                if new_doc:
                    target_row.reference_name = new_doc.name
                    target_row.db_set("reference_name", new_doc.name, update_modified=False)

        # Special: Check fork-join completion for Visa Stamping
        self._check_fork_join_trigger(rows)

    def _check_fork_join_trigger(self, rows):
        """
        Visa Stamping should be auto-created when ALL parallel tracks
        (Medical + PCC) are complete.
        """
        visa_stamping_row = next(
            (r for r in rows if r.process_name == "Visa Stamping"), None
        )
        if not visa_stamping_row or visa_stamping_row.reference_name:
            return  # Already created or not configured

        # Check Medical track (group 1)
        medical_done = False
        for r in rows:
            if r.process_name == "Medical Test" and r.status in ("Fit", "Passed"):
                medical_done = True
                break
            if r.process_name == "Remedical Test" and r.status in ("Fit", "Passed"):
                medical_done = True
                break

        # Check PCC track (group 2)
        pcc_done = False
        for r in rows:
            if r.process_name == "PCC Clearance" and r.status == "Issued":
                pcc_done = True
                break

        # Check Visa Processing
        visa_proc_done = False
        for r in rows:
            if r.process_name == "Visa Processing" and r.status == "Issued":
                visa_proc_done = True
                break

        if medical_done and pcc_done and visa_proc_done:
            if visa_stamping_row.reference_type and not visa_stamping_row.reference_name:
                new_doc = self._create_linked_record(visa_stamping_row)
                if new_doc:
                    visa_stamping_row.reference_name = new_doc.name
                    visa_stamping_row.db_set("reference_name", new_doc.name, update_modified=False)

    def _create_linked_record(self, row):
        """Create a new record of the linked DocType for this process step."""
        doctype = row.reference_type
        if not doctype:
            return None

        meta = frappe.get_meta(doctype)

        # Skip DocTypes that don't have candidate_country_process link
        # (e.g., Medical Appointment uses 'employee' instead)
        if not meta.has_field("candidate_country_process"):
            return None

        # Build the new document with candidate_country_process link
        try:
            new_doc = frappe.new_doc(doctype)
            new_doc.candidate_country_process = self.name

            # Map common fields if they exist on the target DocType
            field_map = {
                "candidate_name": self.candidate_name,
                "passport_number": self.passport_number,
            }
            for field, value in field_map.items():
                if meta.has_field(field) and value:
                    new_doc.set(field, value)

            new_doc.flags.ignore_permissions = True
            new_doc.flags.ignore_mandatory = True
            new_doc.insert(ignore_permissions=True)

            frappe.msgprint(
                f"Auto-created {doctype}: <b>{new_doc.name}</b>",
                indicator="green",
                alert=True,
            )
            return new_doc

        except Exception as e:
            frappe.log_error(
                f"Failed to auto-create {doctype} for {self.name}: {e}",
                "CCP Auto-Create Error"
            )
            return None

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

