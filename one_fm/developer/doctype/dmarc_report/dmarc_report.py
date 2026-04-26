from frappe.model.document import Document
from frappe.utils import formatdate

class DMARCReport(Document):
	def autoname(self):
		# Format: Reporting Organization - DD-MM-YYYY
		# Use begin_date for the date part
		date_str = formatdate(self.begin_date, "dd-MM-yyyy")
		self.name = f"{self.org_name} - {date_str}"
		
		# Ensure uniqueness by adding report_id if there's a collision
		# (Though typically one org only sends one report per period)
