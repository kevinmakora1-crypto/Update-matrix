# -*- coding: utf-8 -*-
# Copyright (c) 2020, ONE FM and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class AccommodationSpace(Document):
	def validate(self):
		self.set_title()
		self.validate_space_type()
		self.update_bed_status()

	def validate_space_type(self):
		if not self.is_new():
			bed_space_type = frappe.db.get_value('Accommodation Space', self.name, 'bed_space_type')
			if bed_space_type != self.bed_space_type:
				self.disable_rest_of_beds()

	def disable_rest_of_beds(self):
		bed_space_capacity = frappe.db.get_value('Accommodation Space', self.name, 'single_bed_capacity')
		if bed_space_capacity and self.single_bed_capacity < bed_space_capacity:
			no_beds_to_disable = bed_space_capacity - self.single_bed_capacity
			disabled_beds = frappe.db.count('Bed', {'disabled': True, 'accommodation_space': self.name})
			fraction = no_beds_to_disable - disabled_beds
			if fraction > 0:
				beds_to_disable = sorted(self.beds,
					key=lambda k: k.disabled == 1)
				i = 0
				for bed in beds_to_disable:
					if i < fraction and bed.status == 'Vacant':
						i += 1
						bed.disabled = True
					elif i >= fraction:
						break

	def update_bed_status(self):
		if self.bed_space_available:
			if not self.is_new():
				self.create_beds_in_space()
			if self.beds:
				for bed in self.beds:
					if self.bed_type and not bed.bed_type:
						bed.bed_type = self.bed_type
					if self.gender and not bed.gender:
						bed.gender = self.gender
					query = """
						update
							tabBed
						set
							disabled=%(disabled)s, bed_type=%(bed_type)s, gender=%(gender)s
						where
							name=%(bed)s
					"""
					filters = {'disabled': bed.disabled, 'gender': bed.gender, 'bed_type': bed.bed_type, 'bed': bed.bed}
					frappe.db.sql(query, filters)

	def after_insert(self):
		self.set("beds", [])
		self.create_beds_in_space()
		self.save(ignore_permissions=True)

	def set_title(self):
		self.title = '-'.join([self.accommodation_name, self.type,
			self.floor_name+' Floor', self.accommodation_space_type])

	def before_insert(self):
		self.validate_no_of_accommodation_space()

	def validate_no_of_accommodation_space(self):
		allowed_no = frappe.db.get_value('Accommodation Unit Space Type', {'parent': self.accommodation_unit,
			'space_type': self.accommodation_space_type}, 'total_number')
		if not allowed_no:
			frappe.throw(_("No {0} is Configured in Accommodation Unit {1}"
				.format(self.accommodation_space_type, self.accommodation_unit)))
		elif frappe.db.count('Accommodation Space',
			{'accommodation_unit': self.accommodation_unit,
				'accommodation_space_type': self.accommodation_space_type}) >= allowed_no:
			frappe.throw(_("Only {0} {1} is allowed in Accommodation Unit {2}"
				.format(allowed_no, self.accommodation_space_type, self.accommodation_unit)))

	def create_beds_in_space(self):
		if self.bed_space_available and self.bed_space_type and self.single_bed_capacity:
			beds_to_create = self.single_bed_capacity - (len(self.beds) if self.beds else 0)
			if beds_to_create > 0:
				for x in range(beds_to_create):
					bed = frappe.new_doc('Bed')
					bed.accommodation_space = self.name
					bed.disabled = False
					bed.bed_space_type = self.bed_space_type
					bed.bed_type = self.bed_type
					bed.gender = self.gender
					bed.save(ignore_permissions=True)
					bed_in_space = self.append('beds')
					bed_in_space.bed = bed.name
					bed_in_space.disabled = bed.disabled
					bed_in_space.bed_type = bed.bed_type
					bed_in_space.gender = bed.gender

	def autoname(self):
		if not self.accommodation_unit:
			frappe.throw(_("Accommodation Unit is required"))

		abbr = self.space_type_abbreviation
		if not abbr:
			# Try to fetch if not set (though it should be fetched automatically)
			if self.accommodation_space_type:
				abbr = frappe.db.get_value("Accommodation Space Type", self.accommodation_space_type, "abbreviation")

		if not abbr:
			abbr = "X"

		counter = get_next_space_number(self.accommodation_unit, abbr)
		self.name = "{}-{}{}".format(self.accommodation_unit, abbr, counter)


def get_next_space_number(accommodation_unit, abbr):
	# Pattern: {accommodation_unit}-{abbr}{number}
	prefix = "{}-{}".format(accommodation_unit, abbr)

	# Get all existing names that start with this prefix
	existing_names = frappe.db.sql("""
		SELECT name FROM `tabAccommodation Space`
		WHERE name LIKE %s
		ORDER BY length(name) DESC, name DESC
		LIMIT 1
	""", (prefix + "%",))

	if existing_names:
		last_name = existing_names[0][0]
		# Extract the number part after the last hyphen + abbr
		# Example: ACC...-U4-B1
		# prefix: ACC...-U4-B
		# We want '1'

		# Safer way: verify it starts with prefix and parse the rest
		if last_name.startswith(prefix):
			suffix = last_name[len(prefix):]
			if suffix.isdigit():
				return int(suffix) + 1

			# If suffix contains other chars (maybe existing data was different?), fall back to regex or split
			# But for new clean pattern, isdigit check is good.
			# Let's try to handle potential edge cases or keep it simple as per prompt specs.

			# Fallback parsing if simple prefix check is risky
			import re
			match = re.search(r"(\d+)$", last_name)
			if match:
				return int(match.group(1)) + 1

	return 1


@frappe.whitelist()
def filter_floor(doctype, txt, searchfield, start, page_len, filters):
	query = """
		select
			floor_name
		from
			`tabAccommodation Unit`
		where
			accommodation = %(accommodation)s and floor_name like %(txt)s
			limit %(start)s, %(page_len)s"""
	return frappe.db.sql(query,
		{
			'accommodation': filters.get("accommodation"),
			'start': start,
			'page_len': page_len,
			'txt': "%%%s%%" % txt
		}
	)