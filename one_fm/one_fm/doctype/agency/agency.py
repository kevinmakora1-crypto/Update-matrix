# -*- coding: utf-8 -*-
# Copyright (c) 2020, ONE FM and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, re
from frappe.model.document import Document
from frappe.contacts.address_and_contact import load_address_and_contact, delete_contact_and_address
from frappe import _
from frappe.utils import getdate, today, add_days
from one_fm.processor import sendemail

class Agency(Document):
	def validate(self):
		if self.agency_website:
			validate_website_adress(self.agency_website)

	def after_insert(self):
		create_supplier_for_agency(self)
		self.create_user_for_agency()

	def create_user_for_agency(self):
		if self.company_email and not frappe.db.exists ("User", self.company_email):
			user = frappe.get_doc({
				"doctype": "User",
				"first_name": self.agency,
				"email": self.company_email,
				"user_type": "Website User"
			})
			user.flags.ignore_permissions = True
			user.add_roles("Supplier")
			user.add_roles("Agency")

	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self)

	def on_trash(self):
		delete_contact_and_address('Customer', self.name)

@frappe.whitelist()
def validate_website_adress(website):
	regex = re.compile(
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

	if(bool(re.match(regex, website))==True):
		return True
	return False

def create_supplier_for_agency(agency):
	if not agency.supplier_code:
		supplier = frappe.new_doc('Supplier')
		supplier.supplier_name = agency.agency
		supplier.country = agency.country
		supplier.website = agency.agency_website
		supplier.supplier_group = 'Services'
		supplier.save(ignore_permissions=True)
		agency.supplier_code = supplier.name

def agency_has_website_permission(doc, ptype, user, verbose=False):
	return True

def inactive_agency_on_license_expiry():
	if not frappe.db.get_single_value("Hiring Settings", "inactive_agency_on_license_expiry"):
		return

	frappe.db.sql("""
		UPDATE 
			`tabAgency`
		SET 
			active = 0
		WHERE 
			active = 1 AND license_validity_date < %s
	""", today())

def inform_license_expiry():
	if not frappe.db.get_single_value("Hiring Settings", "inform_agency_license_expiry_to_recruitment_team"):
		return

	inform_period_days = frappe.db.get_single_value("Hiring Settings", "agency_license_expiry_inform_period_days") or 0

	notify_date = add_days(today(), inform_period_days)
	agencies = frappe.get_all("Agency", filters={"active": 1, "license_validity_date": notify_date}, fields=["name", "license_validity_date", "company_email"])

	if not agencies:
		return

	# Get the notification email from settings
	notification_email = frappe.db.get_single_value("Hiring Settings", "agency_expiry_notification_email")

	if not notification_email:
		return

	# Build the message with all agency details
	agency_details = ""
	for agency in agencies:
		if agency.name:
			agency_details += f"""
				<tr>
					<td style="padding: 8px; border: 1px solid #ddd;">{agency.name}</td>
					<td style="padding: 8px; border: 1px solid #ddd;">{agency.license_validity_date}</td>
					<td style="padding: 8px; border: 1px solid #ddd;">{agency.company_email or 'N/A'}</td>
				</tr>
			"""

	if not agency_details:
		return

	message = f"""
		<p>Dear Team,</p>
		<p>The following agencies have licenses expiring on {notify_date}:</p>
		<table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
			<thead>
				<tr style="background-color: #f2f2f2;">
					<th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Agency Name</th>
					<th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Expiry Date</th>
					<th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Company Email</th>
				</tr>
			</thead>
			<tbody>
				{agency_details}
			</tbody>
		</table>
		<p>Please take the necessary actions to follow up on license renewals.</p>
		<p>Best regards,<br>ONE FM Team</p>
	"""


	sendemail(
		recipients=[notification_email],
		subject=f"Agency License Expiry Notification - {len(agencies)} Agency(ies) Expiring on {notify_date}",
		message=message,
		is_external_mail=True
	)