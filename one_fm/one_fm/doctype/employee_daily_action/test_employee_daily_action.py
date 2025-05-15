# # Copyright (c) 2025, omar jaber and Contributors
# # See license.txt

# import frappe
# from frappe.tests.utils import FrappeTestCase


# class TestEmployeeDailyAction(FrappeTestCase):
# 	pass
# 	def setUp(self):
# 		# Create test employee and manager
# 		self.test_employee = frappe.get_doc({
# 			"doctype": "User",
# 			"email": "test_employee@example.com",
# 			"first_name": "Test",
# 			"last_name": "Employee"
# 		}).insert(ignore_if_duplicate=True)

# 		self.test_manager = frappe.get_doc({
# 			"doctype": "User", 
# 			"email": "test_manager@example.com",
# 			"first_name": "Test",
# 			"last_name": "Manager"
# 		}).insert(ignore_if_duplicate=True)

# 	def test_fetch_todos(self):
# 		# Create test ToDo items for today
# 		todo1 = frappe.get_doc({
# 			"doctype": "ToDo",
# 			"allocated_to": "test_employee@example.com",
# 			"date": frappe.utils.today(),
# 			"description": "Test Todo 1",
# 			"status": "Open",
# 			"type": "General"
# 		}).insert()

# 		todo2 = frappe.get_doc({
# 			"doctype": "ToDo", 
# 			"allocated_to": "test_employee@example.com",
# 			"date": frappe.utils.today(),
# 			"description": "Test Todo 2",
# 			"status": "Closed",
# 			"type": "Technical"
# 		}).insert()

# 		# Create test ToDo items for tomorrow
# 		tomorrow = frappe.utils.add_days(frappe.utils.today(), 1)
# 		todo3 = frappe.get_doc({
# 			"doctype": "ToDo",
# 			"allocated_to": "test_employee@example.com",
# 			"date": tomorrow,
# 			"description": "Test Todo 3",
# 			"status": "Open",
# 			"type": "Project"
# 		}).insert()

# 		todo4 = frappe.get_doc({
# 			"doctype": "ToDo",
# 			"allocated_to": "test_employee@example.com",
# 			"date": tomorrow,
# 			"description": "Test Todo 4",
# 			"status": "Open",
# 			"type": "Routine"
# 		}).insert()

# 		# Create Employee Daily Action
# 		eda = frappe.get_doc({
# 			"doctype": "Employee Daily Action",
# 			"employee_email": "test_employee@example.com",
# 			"manager_email": "test_manager@example.com",
# 			"date": frappe.utils.today()
# 		})
# 		eda.insert()

# 		# Test today's todos were fetched correctly
# 		self.assertEqual(len(eda.todays_plan_and_accomplishments), 2)
# 		today_todo = eda.todays_plan_and_accomplishments[0]
# 		self.assertEqual(today_todo.todo, todo1.name)
# 		self.assertEqual(today_todo.todo_type, "General")
# 		self.assertEqual(today_todo.completed, 0)
# 		self.assertEqual(today_todo.description, "Test Todo 1")

# 		today_todo2 = eda.todays_plan_and_accomplishments[1] 
# 		self.assertEqual(today_todo2.todo, todo2.name)
# 		self.assertEqual(today_todo2.todo_type, "Technical")
# 		self.assertEqual(today_todo2.completed, 1)
# 		self.assertEqual(today_todo2.description, "Test Todo 2")

# 		# Test tomorrow's todos were fetched correctly
# 		self.assertEqual(len(eda.tomorrows_plan), 2)
# 		tomorrow_todo = eda.tomorrows_plan[0]
# 		self.assertEqual(tomorrow_todo.todo, todo3.name)
# 		self.assertEqual(tomorrow_todo.todo_type, "Project")
# 		self.assertEqual(tomorrow_todo.description, "Test Todo 3")

# 		tomorrow_todo2 = eda.tomorrows_plan[1]
# 		self.assertEqual(tomorrow_todo2.todo, todo4.name)
# 		self.assertEqual(tomorrow_todo2.todo_type, "Routine")
# 		self.assertEqual(tomorrow_todo2.description, "Test Todo 4")

# 	def test_create_blockers(self):
# 		# Create Employee Daily Action with blockers
# 		eda = frappe.get_doc({
# 			"doctype": "Employee Daily Action",
# 			"employee_email": "test_employee@example.com", 
# 			"manager_email": "test_manager@example.com",
# 			"date": frappe.utils.today(),
# 			"blocker_table": [
# 				{
# 					"priority": "High",
# 					"problem": "Test Blocker 1"
# 				},
# 				{
# 					"priority": "Medium", 
# 					"problem": "Test Blocker 2"
# 				}
# 			]
# 		})
# 		eda.insert()
# 		eda.submit()

# 		# Verify blockers were created
# 		blockers = frappe.get_all("Blocker", 
# 			filters={
# 				"user": "test_employee@example.com",
# 				"date": frappe.utils.today()
# 			},
# 			fields=["priority", "blocker_details", "status"]
# 		)

# 		self.assertEqual(len(blockers), 2)
# 		self.assertEqual(blockers[0].priority, "High")
# 		self.assertEqual(blockers[0].blocker_details, "Test Blocker 1")
# 		self.assertEqual(blockers[0].status, "Open")

# 	def tearDown(self):
# 		# Clean up test data
# 		frappe.db.sql("delete from `tabToDo` where allocated_to='test_employee@example.com'")
# 		frappe.db.sql("delete from `tabBlocker` where user='test_employee@example.com'")
# 		frappe.delete_doc("User", "test_employee@example.com")
# 		frappe.delete_doc("User", "test_manager@example.com")
