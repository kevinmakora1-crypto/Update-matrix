from frappe import throw, _
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime


class AbsenceCase(Document):
	def validate(self):
		self.validate_formal_hearing_datetime()

	def validate_formal_hearing_datetime(self):
		if not self.formal_hearing_start_datetime:
			return

		# 24-hour notice validation
		now = now_datetime()
		start_datetime = get_datetime(self.formal_hearing_start_datetime)

		# Calculate difference in hours
		diff = (start_datetime - now).total_seconds() / 3600

		if diff < 24:
			throw(_("Formal Hearing Notice must be at least 24 hours prior."))

		# End date validation
		if self.formal_hearing_end_datetime:
			end_datetime = get_datetime(self.formal_hearing_end_datetime)
			if end_datetime <= start_datetime:
				throw(_("Formal Hearing End Datetime must be after Start Datetime."))
