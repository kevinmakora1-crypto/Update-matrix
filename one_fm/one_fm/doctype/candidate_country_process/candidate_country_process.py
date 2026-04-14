# -*- coding: utf-8 -*-
# Copyright (c) 2020, ONE FM and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CandidateCountryProcess(Document):
    def validate(self):
        today = frappe.utils.getdate()
        
        # Chronological cascading anchor
        current_anchor = frappe.utils.getdate(self.start_date) if self.start_date else None
        
        for row in self.agency_process_details:
            # Shift Expected Date dynamically based on the reality of the previous step
            if row.process_name != "Job Offer Issuance":
                if current_anchor and row.duration_in_days is not None:
                    row.expected_date = frappe.utils.add_days(current_anchor, row.duration_in_days)
            
            # Snap anchor to Actual Date if finished, otherwise pass the Expected Date forward
            if row.actual_date:
                current_anchor = frappe.utils.getdate(row.actual_date)
            else:
                current_anchor = frappe.utils.getdate(row.expected_date) if row.expected_date else current_anchor

            # Performance Analytics
            expected = frappe.utils.getdate(row.expected_date) if row.expected_date else None
            actual = frappe.utils.getdate(row.actual_date) if row.actual_date else None
            
            if not actual:
                if expected and today > expected:
                    row.eta_status = "Late"
                else:
                    row.eta_status = "Still Within Time frame"
            else:
                if expected and actual > expected:
                    row.eta_status = "Late"
                elif expected and actual < expected:
                    row.eta_status = "Completed Early"
                else:
                    row.eta_status = "Completed on time"
                    
        # Dynamically mirror Live Plan ETA to the final milestone's edited sequence
        if self.agency_process_details:
            last_step = self.agency_process_details[-1]
            if last_step.expected_date:
                self.live_plan_eta = last_step.expected_date

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
            dt.reference_complete_status_value, dt.reference_complete_status_field, dt.idx, dt.expected_date
        from
            `tabCandidate Country Process` ccp, `tabCandidate Country Process Details` dt
        where
            ccp.current_process_id=dt.name
    """
    ccp_list = frappe.db.sql(query, as_dict=True)
    today = frappe.utils.getdate()

    for ccp in ccp_list:
        delay = 0
        if ccp.expected_date and today > ccp.expected_date:
            delay = (today - ccp.expected_date).days

        if ccp.reference_type and ccp.ccp_name:
            process_doc = frappe.get_doc(ccp.reference_type, {'candidate_country_process': ccp.ccp_name})
            if process_doc:
                if not ccp.reference_name:
                    frappe.db.set_value('Candidate Country Process Details', ccp.dt_name, 'reference_name', process_doc.name)
                
                if process_doc.get(ccp.reference_complete_status_field) == ccp.reference_complete_status_value:
                    frappe.db.set_value('Candidate Country Process Details', ccp.dt_name, 'status', 'Approved')
                    frappe.db.set_value('Candidate Country Process Details', ccp.dt_name, 'actual_date', today)
                    
                    ccp_doc = frappe.get_doc('Candidate Country Process', ccp.ccp_name)
                    
                    # Lock in Permanent Delays
                    if delay > 0:
                        for process_list in ccp_doc.agency_process_details[ccp.idx:]:
                            if process_list.expected_date:
                                process_list.expected_date = frappe.utils.add_days(process_list.expected_date, delay)
                        
                        if ccp_doc.live_plan_eta:
                             ccp_doc.live_plan_eta = frappe.utils.add_days(ccp_doc.live_plan_eta, delay)
                    
                    if len(ccp_doc.agency_process_details) > ccp.idx:
                        for process_list in ccp_doc.agency_process_details:
                            if process_list.idx > ccp.idx and process_list.reference_type:
                                ccp_doc.db_set('current_process_id', process_list.name)
                                break
                    ccp_doc.save(ignore_permissions=True)
                else:
                    # Update Live Plan ETA actively if currently delayed
                    if delay > 0:
                        ccp_doc = frappe.get_doc('Candidate Country Process', ccp.ccp_name)
                        if ccp_doc.planned_eta:
                            ccp_doc.db_set('live_plan_eta', frappe.utils.add_days(ccp_doc.planned_eta, delay))
