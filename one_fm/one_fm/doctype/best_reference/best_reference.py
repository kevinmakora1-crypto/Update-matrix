# -*- coding: utf-8 -*-
# Copyright (c) 2020, ONE FM and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

from frappe.desk.form.assign_to import add as add_assignment

class BestReference(Document):
	

	def after_insert(self):
		self.assign_recruiter()


	def assign_recruiter(self):
		if not self.job_applicant:
			return
		
		try:
			erf = frappe.db.get_value("Job Applicant", self.job_applicant, "one_fm_erf")
			if not erf:
				frappe.log_error(
					message=f"No ERF found for Job Applicant: {self.job_applicant}",
					title="Best Reference - Missing ERF"
				)
				return
			
			assigned_recruiter = frappe.db.get_value("ERF", erf, "recruiter_assigned")
			if not assigned_recruiter:
				frappe.log_error(
					message=f"No recruiter assigned to ERF: {erf}",
					title="Best Reference - Missing Recruiter"
				)
				return
			
			add_assignment({
				'doctype': self.doctype,
				'name': self.name,
				'assign_to': [assigned_recruiter],
				'description': _(
					"The following Best Reference ({0}) needs to be processed. "
					"Kindly proceed with the action."
				).format(self.name)
			})
			
		except Exception as e:
			frappe.log_error(
				message=f"Error assigning recruiter for {self.name}: {str(e)}",
				title="Best Reference Assignment Error"
			)
