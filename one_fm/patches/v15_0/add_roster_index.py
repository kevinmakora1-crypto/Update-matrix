import frappe

def execute():
	add_employee_schedule_index()
	add_operations_shift_index()
	add_attendance_index()
	add_post_schedule_index()

def add_employee_schedule_index():
	frappe.db.add_index("Employee Schedule", ["date", "employee", "operations_role", "roster_type"], "employee_schedule_date")

def add_operations_shift_index():
	frappe.db.add_index("Operations Shift", ["name"], "operations_shift_name")	

def add_attendance_index():
	frappe.db.add_index("Attendance", ["attendance_date", "employee", "operations_shift"], "attendance_date_employee_shift")

def add_post_schedule_index():
	frappe.db.add_index("Post Schedule", ["date", "post_status"], "post_status_date")