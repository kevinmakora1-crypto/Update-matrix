# Copyright (c) 2026, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class SubcontractStaffAttendance(Document):
	def before_validate(self):
		if not self.subcontractor_name and frappe.session.user != "Guest":
			supplier = frappe.db.get_value(
				"User Permission",
				{"user": frappe.session.user, "allow": "Supplier"},
				"for_value"
			)
			if supplier:
				self.subcontractor_name = supplier

	def validate(self):
		if not self.get("subcontractor_staff_attendance_item") and self.subcontractor_name:
			self.fetch_subcontractor_staff()

	@frappe.whitelist()
	def fetch_subcontractor_staff(self):
		if not self.subcontractor_name:
			frappe.throw("Please select a Subcontractor Name first.")
		if not self.from_date or not self.to_date:
			frappe.throw("Please specify From Date and To Date.")

		# Ensure the grid is cleared before fetching new records
		self.set("subcontractor_staff_attendance_item", [])

		# Use the unified API logic that dynamically evaluates actual Attendance records
		items = api_fetch_subcontractor_staff(
			self.subcontractor_name,
			self.from_date,
			self.to_date,
			self.attendance_record_based_on
		)

		if items:
			for row in items:
				self.append("subcontractor_staff_attendance_item", row)


@frappe.whitelist()
def api_fetch_subcontractor_staff(subcontractor_name, from_date, to_date, attendance_record_based_on):
	if not subcontractor_name:
		frappe.throw("Please select a Subcontractor Name first.")
	if not from_date or not to_date:
		frappe.throw("Please specify From Date and To Date.")
	if to_date < from_date:
		frappe.throw("To Date must be greater than or equal to From Date.")

	employees = frappe.get_all(
		"Employee",
		filters={
			"status": "Active",
			"employment_type": "Subcontractor",
			"custom_subcontractor_name": subcontractor_name
		},
		fields=["name", "employee_name"]
	)

	if not employees:
		return []

	# Fetch actual attendance records for these employees in the date range
	employee_ids = [emp.name for emp in employees]
	attendances = frappe.get_all(
		"Attendance",
		filters={
			"employee": ["in", employee_ids],
			"attendance_date": ["between", [from_date, to_date]],
			"docstatus": ["<", 2]
		},
		fields=["employee", "attendance_date", "status", "working_hours"]
	)

	# Map attendances: { employee_id: { day_int: { status: "Present", hours: 8.0 } } }
	attendance_map = {}
	for att in attendances:
		emp = att.employee
		day = getdate(att.attendance_date).day
		
		if emp not in attendance_map:
			attendance_map[emp] = {}
			
		attendance_map[emp][day] = {
			"status": att.status,
			"hours": att.working_hours or 0.0
		}

	items = []
	
	for emp in employees:
		item = {
			"employee": emp.name,
			"employee_id": emp.name,
			"employee_name": emp.employee_name
		}
		
		emp_attendance = attendance_map.get(emp.name, {})
		
		working_days = 0
		off_days = 0

		for i in range(1, 32):
			day_data = emp_attendance.get(i)
			
			if attendance_record_based_on == "Attendance Status":
				status = day_data["status"] if day_data else ""
				item[f"day_{i}"] = status
				if status in ["Present", "Half Day", "Work From Home", "Holiday"]:
					working_days += 1
				elif status in ["Day Off", "Client Day Off"]:
					off_days += 1
			elif attendance_record_based_on == "Shift Hours":
				hours = day_data["hours"] if day_data else 0.0
				item[f"day_{i}_hour"] = hours
				if hours > 0:
					working_days += 1
		
		item["working_days"] = working_days
		item["off_days"] = off_days
		
		items.append(item)
		
	return items
