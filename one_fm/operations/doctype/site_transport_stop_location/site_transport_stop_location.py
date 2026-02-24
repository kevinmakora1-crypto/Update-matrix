import frappe
from frappe.model.document import Document

class SiteTransportStopLocation(Document):
	def validate(self):
		"""Validate required fields based on the selected site arrangement."""

		if self.site_arrangement == "One Location Many Sites":
			missing = []
			if not self.transport_stop_location:
				missing.append("Transport Stop Location")
			if not getattr(self, "sites", None):
				# For child tables, ensure there is at least one entry
				if not self.sites:
					missing.append("Sites")
			if missing:
				frappe.throw(
					"Following fields are required for arrangement 'One Location Many Sites': {0}".format(
						", ".join(missing)
					)
				)

		elif self.site_arrangement == "One Site Many Locations":
			missing = []
			if not self.site:
				missing.append("Site")
			if not getattr(self, "transport_stop_locations", None):
				# For child tables, ensure there is at least one entry
				if not self.transport_stop_locations:
					missing.append("Transport Stop Locations")
			if missing:
				frappe.throw(
					"Following fields are required for arrangement 'One Site Many Locations': {0}".format(
						", ".join(missing)
					)
				)
