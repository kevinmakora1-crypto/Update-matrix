# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate


def create_client_interview_shortlist(employee, project, interview_date=None):
	if not interview_date:
		interview_date = getdate("2025-11-30")

	shortlist = frappe.get_doc(
		{
			"doctype": "Client Interview Shortlist",
			"company": "_Test Company",
			"project": project,
			"interview_date": interview_date,
			"client_interview_employee": [
				{
					"employee": employee,
					"roster_type": "Basic",
				}
			],
		}
	).insert(ignore_permissions=True)
	return shortlist
