# Copyright (c) 2024, omar jaber and contributors
# For license information, please see license.txt

import json, time
import frappe
from frappe.model.document import Document
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count
from frappe.utils import now, validate_email_address
from pypika.terms import Case
from one_fm.api.doc_events import get_employee_user_id

class RelieverAssignment(Document):
	def validate(self):
		self.set_user_ids()
		self.assign_roles()
		self.assign_reportees()
		self.assign_todos()
		self.assign_projects()
		self.assign_operations_site()
		self.assign_routine_tasks()
		self.get_single_doctypes()


	def set_user_ids(self):
		self._employee_user_id = get_employee_user_id(self.on_leave_employee)
		self._reliever_user_id = get_employee_user_id(self.reliever)


	def assign_roles(self):
		employee_on_leave_user = frappe.get_doc("User", self._employee_user_id)
		reliever_user = frappe.get_doc("User", self._reliever_user_id)
		
		roles = frappe._dict({
			"employee_on_leave": frappe._dict({
				"employee": self.on_leave_employee,
				"user_id": self._employee_user_id,
				"role_profile_name": employee_on_leave_user.role_profile_name,
				"roles": [role.role for role in employee_on_leave_user.roles]
			}),
			"reliever": frappe._dict({
				"employee": self.reliever,
				"user_id": self._reliever_user_id,
				"role_profile_name": reliever_user.role_profile_name,
				"roles": [role.role for role in reliever_user.roles]
			}),
		})
		
		# Log data for reversal
		self.add_assigned_documents("User", "Docfield", roles, "role_profile_name")

		roles_to_be_assigned = roles.employee_on_leave.roles + roles.reliever.roles
		# If both have role profile or If reliever has role profile and on leave employee doesn't
		if (employee_on_leave_user.role_profile_name and reliever_user.role_profile_name) or (not employee_on_leave_user.role_profile_name and reliever_user.role_profile_name):
			reliever_user.db_set("role_profile_name", None)

		reliever_user.add_roles(roles_to_be_assigned)


	def assign_reportees(self):
		Employee = DocType("Employee")
		reportees = (
			frappe.qb.from_(Employee)
			.select(Employee.name)
			.where(
				(Employee.reports_to == self.on_leave_employee)
				& (Employee.status == "Active"))
		).run(as_dict=True)

		if len(reportees) > 0:
			# Log data for reversal
			self.add_assigned_documents("Employee", "Docfield", reportees, fieldname="reports_to")

			frappe.qb.update(Employee).set(Employee.reports_to, self.reliever).set(Employee.modified, now()).where(
				Employee.reports_to == self.on_leave_employee).where(Employee.status == "Active").run()


	def assign_todos(self):
		ToDo = DocType("ToDo")
		open_todos = (
			frappe.qb.from_(ToDo)
			.select(ToDo.name)
			.where(
				(ToDo.allocated_to == self._employee_user_id)
				& (ToDo.status == "Open")
			)
		).run(as_dict=True)

		if len(open_todos) > 0:
			# Log data for reversal
			self.add_assigned_documents("ToDo", "Docfield", open_todos, fieldname="allocated_to")

			frappe.qb.update(ToDo).set(ToDo.allocated_to, self._reliever_user_id).set(ToDo.modified, now()).where(
				ToDo.allocated_to == self._employee_user_id).where(ToDo.status == "Open").run()


	def assign_projects(self):
		Project = DocType("Project")
		assigned_projects = (
			frappe.qb.from_(Project)
			.select(Project.name)
			.where(
				(Project.account_manager == self.on_leave_employee)
				& (Project.status == "Open")
			)
		).run(as_dict=True)
		
		if len(assigned_projects) > 0:			
			# Log data for reversal
			self.add_assigned_documents("Project", "Docfield", assigned_projects, fieldname="account_manager")
		
			frappe.qb.update(Project).set(
				Project.account_manager, self.reliever).set(
				Project.manager_name, self.reliever_name).set(
				Project.modified, now()).where(
				Project.account_manager == self.on_leave_employee).where(Project.status == "Open").run()


	def assign_operations_site(self):
		OperationsSite = DocType("Operations Site")
		assigned_sites = (
			frappe.qb.from_(OperationsSite)
			.select(OperationsSite.name)
			.where(
				(OperationsSite.account_supervisor == self.on_leave_employee)
				& (OperationsSite.status == "Active")
			)
		).run(as_dict=True)

		if len(assigned_sites) > 0:	
			# Log data for reversal
			self.add_assigned_documents("Operations Site", "Docfield", assigned_sites, fieldname="account_supervisor")
			
			frappe.qb.update(OperationsSite).set(
				OperationsSite.account_supervisor, self.reliever).set(
				OperationsSite.account_supervisor_name, self.reliever_name).set(
				OperationsSite.modified, now()).where(
				OperationsSite.account_supervisor == self.on_leave_employee).where(OperationsSite.status == "Active").run()


	def assign_routine_tasks(self):
		RoutineTask = DocType("Routine Task")
		routine_tasks = (
			frappe.qb.from_(RoutineTask)
			.select(RoutineTask.name)
			.where((RoutineTask.employee == self.on_leave_employee))
		).run(as_dict=True)
		

		if len(routine_tasks) > 0:
			# Log data for reversal
			self.add_assigned_documents("Routine Task", "Docfield", routine_tasks, fieldname="employee")

			frappe.qb.update(RoutineTask).set(
				RoutineTask.employee, self.reliever).set(
				RoutineTask.employee_name, self.reliever_name).set(
				RoutineTask.modified, now()).where(
				RoutineTask.employee == self.on_leave_employee
			).run()

		# If employee_on_leave is set as Direct Report Reviewer in Routine Task
		routine_tasks_reviewer = (
			frappe.qb.from_(RoutineTask)
			.select(RoutineTask.name)
			.where((RoutineTask.direct_report_reviewer == self.on_leave_employee))
		).run(as_dict=True)
		

		if len(routine_tasks_reviewer) > 0:
			# Log data for reversal
			self.add_assigned_documents("Routine Task", "Docfield", routine_tasks_reviewer, fieldname="direct_report_reviewer")

			frappe.qb.update(RoutineTask).set(
				RoutineTask.direct_report_reviewer, self.reliever).set(
				RoutineTask.direct_report_reviewer_name, self.reliever_name).set(
				RoutineTask.modified, now()).where(
				RoutineTask.direct_report_reviewer == self.on_leave_employee
			).run()



	def add_assigned_documents(self, reference_doctype, based_on, doclist, fieldname=None, reference_docname=None):
		self.append("assigned_documents", {
			"reference_doctype": reference_doctype,
			"based_on": based_on,
			"doclist": json.dumps(doclist, indent=4),
			"fieldname": fieldname,
			"reference_docname": reference_docname
		})
		

	def get_single_doctypes(self):
		Doctype = DocType("DocType")
		Singles = DocType("Singles")
		Docfield = DocType("DocField")

		# Get the list of single doctypes which contain Employee/User link field
		single_doctypes_query = (
			frappe.qb.from_(Docfield)
			.left_join(Doctype)
			.on(Docfield.parent == Doctype.name)
			.select(Docfield.fieldname)
			.where(
				(Doctype.issingle == 1)
				& (Docfield.parent == Doctype.name)
				& (Docfield.parenttype == "DocType")
				& (Docfield.fieldtype == "Link")
				& (Doctype.issingle == 1)
				& (Docfield.options.isin(["Employee", "User"]))
			)
		)

		# Get rows from tabSingles where doctype is Single and employee/user id of on leave employee is set 
		assigned_single_doctypes = (
			frappe.qb.from_(Singles)
			.select("*", )
			.where(
			Singles.field.isin(single_doctypes_query)
			& Singles.value.isin([self._employee_user_id, self.on_leave_employee])	
			)	
		)
		
		assigned_records = assigned_single_doctypes.run(as_dict=True)

		if len(assigned_records) > 0:
			for record in assigned_records:
				if validate_email_address(record.value):
					record.replaced_with = self._reliever_user_id
				else:
					record.replaced_with = self.reliever

				# Log data for reversal
				self.add_assigned_documents(record.doctype, "Docname", record, reference_docname=record.doctype)
				
				frappe.qb.update(Singles).set(
					Singles.value, record.replaced_with
				).where(
					Singles["field"] == record.field
				).where(
					Singles.doctype == record.doctype
				).run()



def assign_responsibilities(leave_application):
	try:
		reliever_assignment = frappe.new_doc("Reliever Assignment")
		reliever_assignment.leave_application = leave_application
		reliever_assignment.save()
	except Exception:
		frappe.log_error(frappe.get_traceback())