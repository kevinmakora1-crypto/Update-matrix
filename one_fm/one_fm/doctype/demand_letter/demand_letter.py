# -*- coding: utf-8 -*-
# Copyright (c) 2020, ONE FM and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, add_days
from one_fm.processor import sendemail

class DemandLetter(Document):
	pass

def get_demand_letter_quota(agency, designation, gender):
	demands = get_demand_letter(agency, designation, gender)
	if not demands:
		return {}

	for demand in demands:
		available_quota = demand.quantity - demand.used_quantity
		if available_quota > 0:
			return demand

	return {}

def get_demand_letter(agency, designation, gender):
	demand_letters = frappe.db.get_all("Demand Letter", {
		"agency": agency,
		"docstatus": 1,
		"valid_till_date": [">=", today()]
	}, ["name"])
	if not demand_letters:
		return []
	return frappe.db.get_all(
		"Demand Letter Demand",
		{
			"parent": ["in", [d.name for d in demand_letters]],
			"designation": designation,
			"gender": gender
		},
		["quantity", "used_quantity", "name"]
	)

def inform_demand_letter_validity_expiry():
	if not frappe.db.get_single_value("Hiring Settings", "inform_demand_letter_validity_expiry_to_recruitment_team"):
		return

	inform_period_days = frappe.db.get_single_value("Hiring Settings", "demand_letter_validity_expiry_inform_period_days") or 0

	notify_date = add_days(today(), inform_period_days)

	demand_letters = frappe.get_all("Demand Letter", filters={"valid_till_date": notify_date}, fields=["name", "valid_till_date", "agency", "agency_name"])

	if not demand_letters:
		return

	notification_email = frappe.db.get_single_value("Hiring Settings", "demand_letter_validity_expiry_notification_email")
	if not notification_email:
		return

	agency_details = ""
	for dl in demand_letters:
		agency_details += f"""
			<tr>
				<td style="padding: 8px; border: 1px solid #ddd;">{dl.name}</td>
				<td style="padding: 8px; border: 1px solid #ddd;">{dl.valid_till_date}</td>
				<td style="padding: 8px; border: 1px solid #ddd;">{dl.agency_name}</td>
			</tr>
		"""

	message = f"""
		<p>Dear Recruitment Team,</p>
		<p>The following Demand Letter(s) are expiring on ({notify_date}):</p>
		<table style="border-collapse: collapse; width: 100%;">
			<tr>
				<th style="padding: 8px; border: 1px solid #ddd;">Demand Letter</th>
				<th style="padding: 8px; border: 1px solid #ddd;">Validity End Date</th>
				<th style="padding: 8px; border: 1px solid #ddd;">Requesting Agency</th>
			</tr>
			{agency_details}
		</table>
		<p>Please take the necessary actions.</p>
		<p>Best Regards,<br/>ONE FM System</p>
	"""

	sendemail(
		recipients=[notification_email],
		subject=f"Demand Letter Validity Expiry Notification - {len(demand_letters)} Demand Letter(s) Expiring on {notify_date}",
		message=message,
		is_external_mail=True
	)