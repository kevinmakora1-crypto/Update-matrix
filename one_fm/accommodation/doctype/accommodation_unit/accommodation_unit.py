# -*- coding: utf-8 -*-
# Copyright (c) 2020, ONE FM and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class AccommodationUnit(Document):
	def validate(self):
		self.set_title()

	def before_insert(self):
		self.validate_no_of_accommodation_unit()

	def validate_no_of_accommodation_unit(self):
		allowed_no_of_unit = frappe.db.get_value('Accommodation', self.accommodation, 'total_no_of_accommodation_unit')
		if frappe.db.count('Accommodation Unit', {'accommodation': self.accommodation}) >= allowed_no_of_unit:
			frappe.throw(_("Only {0} Accommodation Unit is allowed in Accommodation {1}"
				.format(allowed_no_of_unit, self.accommodation_name)))

	def set_title(self):
		self.title = '-'.join([self.accommodation_name, self.type, self.floor_name+' Floor'])

	def autoname(self):
		if not self.accommodation:
			frappe.throw(_("Accommodation is required"))
		if not self.floor:
			# If floor is not set, try to fetch it from floor_name
			if self.floor_name:
				self.floor = frappe.db.get_value("Floor", self.floor_name, "floor")

			if not self.floor:
				frappe.throw(_("Floor is required"))

		counter = get_next_unit_number(self.accommodation, self.floor)
		self.name = "{}-F{}-U{}".format(self.accommodation, self.floor, counter)


def get_next_unit_number(accommodation, floor):
	# Pattern: {accommodation}-F{floor}-U%
	prefix = "{}-F{}-U".format(accommodation, floor)

	# Get all existing names that start with this prefix
	existing_names = frappe.db.sql("""
		SELECT name FROM `tabAccommodation Unit`
		WHERE name LIKE %s
		ORDER BY length(name) DESC, name DESC
		LIMIT 1
	""", (prefix + "%",))

	if existing_names:
		last_name = existing_names[0][0]
		# Extract the number part after the last 'U'
		parts = last_name.split('-U')
		if len(parts) > 1:
			try:
				return int(parts[-1]) + 1
			except ValueError:
				pass

	return 1

