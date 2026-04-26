from frappe.model.document import Document
from frappe.utils import formatdate, cint

class DMARCReport(Document):
	def autoname(self):
		# Use report_id as the name to guarantee uniqueness
		# The report_id is a unique hash from the reporting organization
		if self.report_id:
			self.name = self.report_id
		else:
			# Fallback: let frappe generate a hash
			pass

	def before_save(self):
		# Set a human-readable title for display purposes
		if self.org_name and self.begin_date:
			date_str = formatdate(self.begin_date, "dd-MM-yyyy")
			self.title = f"{self.org_name} - {date_str}"
