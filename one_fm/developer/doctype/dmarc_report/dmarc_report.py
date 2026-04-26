from frappe.model.document import Document
from frappe.utils import formatdate, cint

class DMARCReport(Document):
	def autoname(self):
		# Format: Reporting Organization - DD-MM-YYYY
		if self.org_name and self.begin_date:
			date_str = formatdate(self.begin_date, "dd-MM-yyyy")
			self.name = f"{self.org_name} - {date_str}"
		else:
			# Fallback to report_id if data is missing
			self.name = self.report_id
