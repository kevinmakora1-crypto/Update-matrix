# Copyright (c) 2013, ONE FM and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	total_row = get_total_row(data)
	data.append(total_row)
	return columns, data


def get_columns():
    return [
        _("Code/Rerf") + ":Link/Accommodation:100",
        _("Accommodation Name") + ":Data:180",
		_("Total Bed") + ":Data:100",
		_("Occupied") + ":Data:120",
		_("Occupied Temporarily") + ":Data:180",
		_("Booked") + ":Data:100",
		_("Temporary Booked") + ":Data:150",
		_("Vacant") + ":Data:100",
		_("Occupied %") + ":Percent:100",
		_("Vacant %") + ":Percent:100"
    ]

def get_data(filters):
	data=[]
	acc_list=frappe.db.sql("""select * from `tabAccommodation`""",as_dict=1)
	for acc in acc_list:
		filters['accommodation'] = acc.name
		filters['disabled'] = 0
		total_no_of_bed_space = frappe.db.count('Bed', filters)
		# filters['status'] = 'Occupied'
		# occupied_bed = frappe.db.count('Bed', filters)
		occupied_bed = get_submitted_occupied_count(filters, is_temp=False)

		# filters['status'] = 'Occupied Temporarily'
		# occupied_temporarily = frappe.db.count('Bed', filters)
		occupied_temporarily = get_submitted_occupied_count(filters, is_temp=True)
		filters['status'] = 'Booked'
		booked_bed = frappe.db.count('Bed', filters)
		filters['status'] = 'Vacant'
		vaccant_bed = frappe.db.count('Bed', filters)
		filters['status'] = 'Temporary Booked'
		temporary_booked_bed = frappe.db.count('Bed', filters)
		filters.pop('status')
		occupied_percent = 0
		if total_no_of_bed_space > 0:
			occupied_percent = ((occupied_bed+occupied_temporarily)*100)/total_no_of_bed_space
		vacant_percent = 0
		if total_no_of_bed_space > 0:
			vacant_percent = (vaccant_bed*100)/total_no_of_bed_space
		row = [
			acc.name,
			acc.accommodation,
			total_no_of_bed_space,
			occupied_bed,
			occupied_temporarily,
			booked_bed,
			temporary_booked_bed,
			vaccant_bed,
			occupied_percent,
			vacant_percent
		]
		data.append(row)

	return data

def get_total_row(data):
	total_beds = sum(row[2] for row in data)
	total_occupied = sum(row[3] for row in data)
	total_occupied_temp = sum(row[4] for row in data)
	total_booked = sum(row[5] for row in data)
	total_temp_booked = sum(row[6] for row in data)
	total_vacant = sum(row[7] for row in data)

	# Weighted percent calculations
	total_occupied_percent = (total_occupied + total_occupied_temp) * 100 / total_beds if total_beds else 0
	total_vacant_percent = total_vacant * 100 / total_beds if total_beds else 0

	return [
		"Total", "",  # First 2 columns are blank or "Total"
		total_beds,
		total_occupied,
		total_occupied_temp,
		total_booked,
		total_temp_booked,
		total_vacant,
		total_occupied_percent,
		total_vacant_percent,
	]


def get_submitted_occupied_count(filters, is_temp=False):
    """
    Count occupied beds based on SUBMITTED (docstatus=1) Accommodation Checkin Checkout documents.
    This avoids counting beds reserved by Draft check-ins.
    """
    conditions = []
    values = {}

    # Basic Bed filters
    if filters.get('accommodation'):
        conditions.append("b.accommodation = %(accommodation)s")
        values['accommodation'] = filters.get('accommodation')
    
    if filters.get('bed_space_type'):
        conditions.append("b.bed_space_type = %(bed_space_type)s")
        values['bed_space_type'] = filters.get('bed_space_type')

    if filters.get('gender'):
        conditions.append("b.gender = %(gender)s")
        values['gender'] = filters.get('gender')
        
    conditions.append("b.disabled = 0")

    # Policy condition for Temporary vs Permanent
    if is_temp:
        # Temporary: Policy is MISSING or EMPTY
        policy_condition = "(c.attach_print_accommodation_policy IS NULL OR c.attach_print_accommodation_policy = '')"
    else:
        # Permanent: Policy is PRESENT
        policy_condition = "(c.attach_print_accommodation_policy IS NOT NULL AND c.attach_print_accommodation_policy != '')"

    query = f"""
        SELECT count(distinct b.name)
        FROM `tabBed` b
        INNER JOIN `tabAccommodation Checkin Checkout` c ON b.name = c.bed
        WHERE
            c.docstatus = 1  -- Only Submitted Checkins
            AND c.type = 'IN' 
            AND c.checked_out = 0 
            AND {policy_condition}
            AND {" AND ".join(conditions)}
    """
    
    result = frappe.db.sql(query, values)
    return result[0][0] if result else 0
