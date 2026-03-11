# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class PathfinderLog(Document):
	def before_save(self):
		self.set_initial_time_log()
		self.update_time_log()

	def set_initial_time_log(self):
		if not self.is_new():
			return
		self.time_log = []
		self.add_time_log()

	def update_time_log(self):
		if self.is_new():
			return
		old_doc = self.get_doc_before_save()
		if old_doc and old_doc.workflow_state != self.workflow_state:
			last_log = None
			if self.time_log:
				last_log = self.time_log[-1]

			if last_log and last_log.state == old_doc.workflow_state and not last_log.end_time:
				last_log.end_time = now_datetime()
				last_log.duration = frappe.utils.time_diff_in_seconds(
					last_log.end_time, last_log.start_time
				)

			if self.workflow_state != "Completed":
				self.add_time_log()

	def add_time_log(self):
		self.append(
			"time_log",
			{
				"state": self.workflow_state,
				"start_time": now_datetime()
			}
		)