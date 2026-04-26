import frappe
from frappe.model.document import Document
from frappe.utils import formatdate, getdate, cint

class DMARCReport(Document):
	def autoname(self):
		# Name format: "Reporting Organization - DD-MM-YYYY"
		if self.org_name and self.begin_date:
			date_str = formatdate(getdate(self.begin_date), "dd-MM-yyyy")
			base_name = f"{self.org_name} - {date_str}"

			# Handle duplicates (e.g. same org sends multiple reports per day)
			if not frappe.db.exists("DMARC Report", base_name):
				self.name = base_name
			else:
				# Append counter for uniqueness
				count = 1
				while frappe.db.exists("DMARC Report", f"{base_name}-{count}"):
					count += 1
				self.name = f"{base_name}-{count}"
		else:
			# Fallback to report_id if date/org is missing
			self.name = self.report_id

		# Also set title for display
		self.title = self.name
