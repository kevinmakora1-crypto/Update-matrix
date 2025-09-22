# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt
import calendar

import frappe
from frappe.model.document import Document
from frappe.utils import (getdate, get_first_day, get_last_day, add_days)


class ContractComplianceChecker(Document):
	pass



class GenerateContractComplianceChecker:
	
	def __init__(self):
		self.data = []
		self.monthly_info = self.get_month_info()
		self.week_info = self.get_week_info()
		self.yesterday = frappe.utils.add_days(frappe.utils.today(), -1)
		self.day_before_yesterday = frappe.utils.add_days(frappe.utils.today(), -2)
		self.today = frappe.utils.today()

	def get_contracts_list(self):
		return frappe.db.sql("""
			SELECT ci.parent, ci.count, ci.item_code, ci.days_off_category, ci.no_of_days_off 
			FROM `tabContract Item` ci
			INNER JOIN `tabContracts` c ON ci.parent = c.name
			WHERE ci.rate_type_off = %s AND ci.parentfield = %s AND ci.parenttype = %s
			AND c.workflow_state = %s
		""", ("Days Off", "items", "Contracts", "Active"), as_dict=1)
	
	def get_operations_role(self, sale_item):
		return frappe.db.get_list('Operations Role', {'sale_item': sale_item, 'status': 'Active'}, pluck='name')
	
	def get_total_count(self, operations_role, is_monthly=True):
		if not operations_role:
			return 0
		
		if is_monthly:
			if self.day_before_yesterday >= self.monthly_info['first_day']:
				attendance_count = frappe.db.count('Attendance', {
					'roster_type': "Basic",
					"status": "Present",
					"attendance_date": ["between", [self.monthly_info['first_day'], self.day_before_yesterday]],
					"operations_role": ["in", operations_role]
				})
			else:
				attendance_count = 0
			
			if self.yesterday <= self.monthly_info['last_day']:
				schedule_count = frappe.db.count('Employee Schedule', {
					'roster_type': "Basic",
					"employee_availability": "Working",
					"date": ["between", [self.yesterday, self.monthly_info['last_day']]],
					"operations_role": ["in", operations_role]
				})
			else:
				schedule_count = 0
				
		else:
			if self.day_before_yesterday >= self.week_info['first_day']:
				attendance_count = frappe.db.count('Attendance', {
					'roster_type': "Basic",
					"status": "Present",
					"attendance_date": ["between", [self.week_info['first_day'], self.day_before_yesterday]],
					"operations_role": ["in", operations_role]
				})
			else:
				attendance_count = 0
			
			if self.yesterday <= self.week_info['last_day']:
				schedule_count = frappe.db.count('Employee Schedule', {
					'roster_type': "Basic",
					"employee_availability": "Working",
					"date": ["between", [self.yesterday, self.week_info['last_day']]],
					"operations_role": ["in", operations_role]
				})
			else:
				schedule_count = 0
		
		return attendance_count + schedule_count
	
	def calculate_compliance(self, contract_data, is_monthly=True):
		operations_role = self.get_operations_role(contract_data.item_code)
		total_count = self.get_total_count(operations_role, is_monthly)
		
		if is_monthly:
			working_days = self.monthly_info['days_in_month'] - contract_data.no_of_days_off
			from_date = self.monthly_info['first_day']
			to_date = self.monthly_info['last_day']
		else:
			working_days = 7 - contract_data.no_of_days_off
			from_date = self.week_info['first_day']
			to_date = self.week_info['last_day']
		
		expected_schedule_count = working_days * contract_data.count
		
		if total_count != expected_schedule_count:
			return True, {
				'from_date': from_date,
				'to_date': to_date,
				'comment': self.set_comment(expected_schedule_count, total_count),
				'contract': contract_data.parent,
				'sale_item': contract_data.item_code,
			}
		return False, {}
	
	@staticmethod
	def set_comment(expected_total, actual_total):
		diff = actual_total - expected_total
		if diff >= 1:
			return f"More Schedules Created, expected {expected_total}, created {actual_total}"
		elif diff <= -1:
			return f"Less Schedules Created, expected {expected_total}, created {actual_total}"
		return ""
	
	@staticmethod
	def get_month_info():
		date = getdate(frappe.utils.today())
		return {
			'first_day': get_first_day(date),
			'last_day': get_last_day(date),
			'days_in_month': calendar.monthrange(date.year, date.month)[1]
		}
	
	@staticmethod
	def get_week_info():
		date = getdate(frappe.utils.today())
		weekday = date.weekday()
		days_to_sunday = (weekday + 1) % 7
		first_day = add_days(date, -days_to_sunday)
		
		return {
			'first_day': first_day,
			'last_day': add_days(first_day, 6)
		}
	
	def create_compliance_checker(self, contract, compliance_details):
		contract_details = frappe.db.get_value("Contracts", contract, 
			["client", "project", "project.account_manager"], as_dict=1)
		
		doc = frappe.get_doc({
			"doctype": "Contract Compliance Checker",
			"project": contract_details.project,
			"contract": contract,
			"project_manager": contract_details.account_manager,
			"check_date": self.today,
			"client": contract_details.client,
		})
		
		for detail in compliance_details:
			doc.append("items", {
				"item": detail.get("sale_item"),
				"from_date": detail.get("from_date"),
				"to_date": detail.get("to_date"),
				"comment": detail.get("comment")
			})
		
		doc.insert(ignore_permissions=True)
	
	def execute(self):
		contracts_list = self.get_contracts_list()
		
		for contract in contracts_list:
			if contract.days_off_category == "Monthly":
				status, data = self.calculate_compliance(contract, is_monthly=True)
			elif contract.days_off_category == "Weekly":
				status, data = self.calculate_compliance(contract, is_monthly=False)
			else:
				continue
			
			if status:
				self.data.append(data)
		
		contract_groups = {}
		for item in self.data:
			contract = item['contract']
			if contract not in contract_groups:
				contract_groups[contract] = []
			contract_groups[contract].append(item)
		
		for contract, compliance_details in contract_groups.items():
			self.create_compliance_checker(contract, compliance_details)


def generate_contract_compliance_checker():
	try:
		generator = GenerateContractComplianceChecker()
		generator.execute()
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Contract Compliance Checker Generation Failed")
		pass