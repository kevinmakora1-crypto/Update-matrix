# Copyright (c) 2023, omar jaber and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
import calendar
from frappe.desk.form.assign_to import add as add_assignment, DuplicateToDoError
from frappe import _
from datetime import datetime,timedelta
from one_fm.overrides.assignment_rule import get_assignment_rule_description
from croniter import croniter, CroniterBadCronError
from frappe.utils import (
	getdate,
 	get_datetime,
	today,
 	now_datetime,
	get_last_day
)

class ProcessTask(Document):
	def validate(self):
		self.validate_dates()
		self.validate_frequency()
		self.validate_method()
		if not all([self.is_active, self.method, self.get_frequency_for_scheduled_event()]):
			self.clear_scheduled_events()

	def validate_dates(self):
		if self.end_date:
			self.validate_from_to_dates("start_date", "end_date")

		if self.end_date == self.start_date:
			frappe.throw(
				_("{0} should not be same as {1}").format(frappe.bold("End Date"), frappe.bold("Start Date"))
			)

	def validate_frequency(self):
		""" Validate the corresponding date or cron data in the frequency field """
		self.validate_cron()
		if self.frequency == "Weekly":
			self.validate_weekly()
		elif self.frequency=="Monthly":
			self.validate_monthly()
		else:
			self.set_frequency_option()

	def validate_cron(self):
		"""
			Validate the value in the cron format field to ensure it is a valid cron
		"""
		if self.frequency != "Cron":
			return

		is_new_or_modified = self.is_new() or (
			not self.is_new() and self.get_doc_before_save().get("cron_format") != self.cron_format
		)

		if is_new_or_modified:
			try:
				croniter(self.cron_format)
			except CroniterBadCronError:
				frappe.log_error(title = "Error Validating Cron",message=frappe.get_traceback())
				frappe.throw("Invalid Cron Set. Check Error Log for more details.")

	def validate_weekly(self):
		if self.frequency!="Weekly":
			return
		if not self.repeat_on_days:
			frappe.throw("Please set the days of the week to trigger process")

		# Extract all days
		repeat_on_days_pre_format = [item.day for item in self.repeat_on_days]

		# Remove duplicates using set
		repeat_on_days_post_format = list(set(repeat_on_days_pre_format))

		# Only reset if new items were present
		if len(repeat_on_days_post_format)!=len(repeat_on_days_pre_format):
			self.repeat_on_days = []
			for each in repeat_on_days_post_format:
				self.append('repeat_on_days', {'day': each})

	def validate_monthly(self):
		if self.frequency != "Monthly":
			return

		if self.repeat_on_last_day:
			self.repeat_on_day = None
		else:
			if not self.repeat_on_day or self.repeat_on_day not in range(1, 32):
				frappe.throw("Please set a valid day of the month (1–31).")

	def set_frequency_option(self):
		""" To accommodate the options like `Weekly on Wednesday` or `Monthly on second Wednesday` based on the date """
		if not self.frequency:
			return
		frequency_field = next(
			(df for df in frappe.get_meta("Process Task").fields if df.fieldname == "frequency"),
			None
		)
		if frequency_field:
			frequency_field.options = ""

	def validate_method(self):
		if not(self.is_automated and self.is_erp_task):
			self.method = ""

	def clear_scheduled_events(self):
		"""Deletes existing scheduled jobs by Server Script if self.event_frequency or self.cron_format has changed"""
		scheduled_job_type = frappe.db.exists("Scheduled Job Type", {"process_task": self.name})
		if scheduled_job_type:
			frappe.delete_doc("Scheduled Job Type", scheduled_job_type, delete_permanently=1)

	def after_insert(self):
		if self.is_active == 1 and self.task_type == "Routine" and not self.is_erp_task:
			self.set_task_and_auto_repeat()

	@frappe.whitelist()
	def set_task_and_auto_repeat(self):
		task = self.set_task_for_process_task()
		if task:
			self.set_auto_repeat_for_task(task)

	def set_task_for_process_task(self):
		if self.task:
			task = frappe.new_doc('Task')
			task.subject = (self.task[slice(78)]+"...") if len(self.task) > 80 else self.task
			task.description = self.task
			task.type = self.task_type
			employee_user = frappe.get_value('Employee', self.employee, 'user_id')
			task.append('custom_assigned_to', {"user": employee_user})

			if self.remark:
				task.description += "<br/><br/><b>Remarks:</b><br/>" + self.remark
			task.expected_time = self.hours_per_frequency
			if self.erp_document:
				task.routine_erp_document = self.erp_document
			task.save(ignore_permissions=True)
			self.db_set('task_reference', task.name)
			return task.name
		return self.task_reference

	def set_auto_repeat_for_task(self, task):
		if not self.auto_repeat_reference:
			auto_repeat = frappe.new_doc('Auto Repeat')
			auto_repeat.reference_doctype = "Task"
			auto_repeat.reference_document = task
			auto_repeat.start_date = self.start_date
			auto_repeat.frequency = self.frequency
			if self.end_date:
				auto_repeat.end_date = self.end_date
			if auto_repeat.frequency == 'Monthly':
				if self.repeat_on_last_day:
					auto_repeat.repeat_on_last_day = self.repeat_on_last_day
				elif self.repeat_on_day:
					auto_repeat.repeat_on_day = self.repeat_on_day
				else:
					day_in_frequency = int(day_of_the_frequency(auto_repeat.frequency, self.start_date))
					if day_in_frequency > 28 and auto_repeat.frequency == 'Monthly':
						day_in_frequency = 28
					auto_repeat.repeat_on_day = day_in_frequency
			if auto_repeat.frequency == 'Weekly':
				if self.repeat_on_days and len(self.repeat_on_days) > 0:
					for item in self.repeat_on_days:
						repeat_on_days = auto_repeat.append('repeat_on_days')
						repeat_on_days.day = item.day
				else: # Weekly on the selected start date day
					repeat_on_days = auto_repeat.append('repeat_on_days')
					repeat_on_days.day = day_of_the_frequency(auto_repeat.frequency, self.start_date)
			auto_repeat.save(ignore_permissions=True)
			self.db_set('auto_repeat_reference', auto_repeat.name)

	def on_update(self):
		self.update_assignment_rule_for_doc_in_process()
		if not self.is_active and self.task_type != "Routine" and self.is_erp_task == 1:
			self.remove_task_and_auto_repeat()
		if self.is_active == 1 and self.task_type == "Routine" and self.is_erp_task == 1 and self.method:
			self.setup_scheduler_events()

	def update_assignment_rule_for_doc_in_process(self):
		if self.is_erp_task and self.process_name and self.employee_user:
			# Get routine task process to get the documents linked with the routine task
			rt_process = frappe.get_doc('Process', self.process_name)
			document_names = False
			common_assignment_rule_linked_docs = []
			# Iterate the documents list linked with the routine task process to update the assignment rule
			if hasattr(rt_process, 'erp_document'):
				for erp_doc in rt_process.erp_document:
					'''
						Check if assignment rule exists without routine task link for the document,
						do not create the assignment rule linked with routine task for the document.
					'''
					if frappe.db.exists('Assignment Rule', {'document_type': erp_doc.process_task_document, 'custom_process_task': ['is', 'not set']}):
						common_assignment_rule_linked_docs.append(erp_doc.process_task_document)
						continue

					if document_names:
						document_names += ", "+erp_doc.process_task_document
					else:
						document_names = erp_doc.process_task_document
					# Check if assignment rule exists for the routine task and the document
					assignment_rule_exists = frappe.db.exists('Assignment Rule', {'document_type': erp_doc.process_task_document, 'custom_process_task': self.name})
					assignment_rule = False
					'''
						If assignment rule exists with the filters and employee got changed in the routine task,
						then get the assignment rule object and set the users linked in assignment rule to null
					'''
					if assignment_rule_exists and self.has_value_changed("employee"):
						assignment_rule = frappe.get_doc('Assignment Rule', assignment_rule_exists)
						assignment_rule.users = []
					# If no assignment rule exists for the filters, create new assignment rule object
					else:
						assignment_rule = frappe.new_doc('Assignment Rule')
						assignment_rule.name = "{0}-{1}".format(self.name, erp_doc.process_task_document)
						assignment_rule.document_type = erp_doc.process_task_document
						assignment_rule.description = get_assignment_rule_description(erp_doc.process_task_document)
						assignment_rule.assign_condition = 'docstatus == 0'
						assignment_rule.rule = 'Round Robin'
						assignment_rule.custom_process_task = self.name

						days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
						for day in days:
							assignment_days = assignment_rule.append('assignment_days')
							assignment_days.day = day

					# If assignment rule object exists, set user of employee selected in the routine task as the users of assignment rule and save it.
					if assignment_rule:
						users = assignment_rule.append('users')
						users.user = self.employee_user
						assignment_rule.save(ignore_permissions=True)
						frappe.msgprint(_("Assignment rules are Updated for the document(s): {0}".format(document_names)), alert=True, indicator='green')

			# Notify the user by msg print about the assignment rule not linked with routine task
			if common_assignment_rule_linked_docs and len(common_assignment_rule_linked_docs) > 0:
				msg = _("No Assignment Rule created for the Rotine task for the lsited documents, since common Assignment Rule linked to these documents: {0}".format(", ".join(common_assignment_rule_linked_docs)))
				frappe.msgprint(msg, alert=True, indicator='orange')

	@frappe.whitelist()
	def remove_task_and_auto_repeat(self):
		task_reference = self.task_reference
		auto_repeat_reference = self.auto_repeat_reference
		if self.auto_repeat_reference:
			self.db_set('auto_repeat_reference', '')
			frappe.delete_doc('Auto Repeat', auto_repeat_reference)

		if self.task_reference:
			self.db_set('task_reference', '')
			frappe.delete_doc('Task', task_reference)

		self.add_comment("Info", "Remove Task {0} and Auto Repeat {1}".format(task_reference, auto_repeat_reference))

	def setup_scheduler_events(self):
		frequency = self.get_frequency_for_scheduled_event()
		scheduled_job_type = frappe.db.get_value("Scheduled Job Type", {"method": self.method})

		if not frequency:
			if scheduled_job_type:
				self.clear_scheduled_events()
			return

		cron_format = self.get_cron_format()

		if not scheduled_job_type:
			frappe.get_doc(
				{
					"doctype": "Scheduled Job Type",
					"method": self.method,
					"frequency": frequency,
					"process_task": self.name,
					"cron_format": cron_format,
				}
			).insert()
			frappe.msgprint(_("Enabled scheduled execution for process task {0}").format(self.name))
			return

		job_doc = frappe.get_doc("Scheduled Job Type", scheduled_job_type)
		if job_doc.frequency != frequency or job_doc.cron_format != cron_format:
			job_doc.frequency = frequency
			job_doc.cron_format = cron_format
			job_doc.save()
			frappe.msgprint(_("Scheduled execution for process task {0} has updated").format(self.name))

	def get_frequency_for_scheduled_event(self):
		weekday = getdate().strftime('%A')
		if self.frequency == f"Monthly on second {weekday}":
			return False
		if self.frequency == "Monthly":
			if self.repeat_on_last_day:
				return False
			return "Cron"
		if self.frequency == "Daily":
			return "Daily"
		if self.frequency:
			return "Cron"
		return False

	def get_cron_format(self):
		day_map = {
			"Sunday": "0", "Monday": "1", "Tuesday": "2", "Wednesday": "3",
			"Thursday": "4", "Friday": "5", "Saturday": "6"
		}
		if self.frequency == "Cron":
			return self.cron_format
		if self.frequency == "Weekly":
			repeat_on_days = ",".join(day_map.get(item.day) for item in self.repeat_on_days)
			return f"0 0 * * {repeat_on_days}"
		if self.frequency == "Monthly":
			return f"0 0 {self.repeat_on_day} * *"
		weekday = getdate().strftime('%A')
		if self.frequency == f"Weekly on {weekday}":
			return f"0 0 * * {day_map.get(weekday)}"

		return ""

@frappe.whitelist()
def filter_routine_document(doctype, txt, searchfield, start, page_len, filters):
	query = """
		select
			routine_task_document
		from
			`tabRoutine Task Document`
		where
			parenttype='Process' and parent=%(parent)s and routine_task_document like %(txt)s
			limit %(start)s, %(page_len)s
	"""
	return frappe.db.sql(query,
		{
			'parent': filters.get("parent"),
			'start': start,
			'page_len': page_len,
			'txt': "%%%s%%" % txt
		}
	)

def day_of_the_frequency(frequency, date):
	week_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
	if frequency == 'Monthly':
		return getdate(date).strftime("%d")
	if frequency == 'Weekly':
		return week_map[getdate(date).weekday()]
	return 1

def create_task_on_monthly_on_day():
	try:
		"""Create task for the task process with a monthly on the day(day of the start date) frequency"""
		today = get_datetime()
		day_name = today.strftime("%A")
		second_weekday = get_second_weekday(today.year, today.month, day_name)

		if not second_weekday or second_weekday != today.date():
			return

		monthly_on_day_process_tasks = frappe.db.sql("""
			SELECT name
			FROM `tabProcess Task`
			WHERE
				is_active = 1 AND frequency = %(frequency)s AND is_erp_task = 0 AND task_type = 'Routine'
				AND (
					(end_date IS NOT NULL AND DATE(%(today)s) BETWEEN DATE(start_date) AND DATE(end_date))
					OR (end_date IS NULL AND DATE(%(today)s) >= DATE(start_date))
				)
			""", {"frequency": f"Monthly on second {day_name}", "today": today}, as_dict=True)

		for process_task in monthly_on_day_process_tasks:
			process_task_doc = frappe.get_doc("Process Task", process_task.name)
			process_task_doc.set_task_for_process_task()
			process_task_doc.db_set('last_execution',now_datetime())
			frappe.db.commit()
	except:
		frappe.log_error(title = "Error Creating Tasks from Process Task", message = frappe.get_traceback())

def create_task_on_cron_process_task():
	"""Trigger all the Task creating process tasks for the day for cron based process tasks"""
	try:
		time_now = now_datetime()
		today = get_datetime()

		cron_process_tasks = frappe.db.sql("""
						SELECT
							name, cron_format, last_execution
						FROM
							`tabProcess Task`
						WHERE
							is_active =1 AND frequency = 'Cron' AND is_erp_task = 0 AND task_type = 'Routine'
						AND (
							(end_date IS NOT NULL AND DATE(%(today)s) BETWEEN DATE(start_date) AND DATE(end_date))
							OR (end_date IS NULL AND DATE(%(today)s) >= DATE(start_date))
						)
					""", {"today": today}, as_dict=True)
		for process_task in cron_process_tasks:
			last_executed =  process_task.get("last_execution") or datetime.min
			try:
				cron_time = croniter(process_task.get("cron_format"), time_now).get_prev(datetime)
				if cron_time > last_executed and time_now >= cron_time:
					process_task_doc = frappe.get_doc("Process Task", process_task.name)
					process_task_doc.set_task_for_process_task()
					process_task_doc.db_set('last_execution',now_datetime())
					frappe.db.commit()
			except Exception as e:
				frappe.log_error(message = frappe.get_traceback(), title = f"Process Task - Cron Error for {process_task.name}")
				continue
	except:
		frappe.log_error(title = "Error Creating Task",message=frappe.get_traceback())

def trigger_method_from_monthly_on_day_process_task():
	today = getdate()
	weekday = today.strftime('%A') # Eg. 'Monday'
	frequency = f"Monthly on second {weekday}"

	second_weekday = get_second_weekday(today.year, today.month, weekday)

	if today != second_weekday:
		return

	process_tasks = frappe.db.sql("""
			SELECT
				name, method, frequency
			FROM
				`tabProcess Task`
			WHERE
				is_active = 1 AND task_type = 'Routine' AND is_erp_task = 1 AND is_automated = 1
				AND frequency = %(frequency)s AND start_date <= %(today)s AND (end_date IS NULL OR end_date > %(today)s)
		""", {"frequency": frequency, "today": today}, as_dict=True)

	for task in process_tasks:
		if not task.method:
			frappe.logger().info(f"[Process Task] Skipping {task.name} - No method defined")
			continue

		method_path = frappe.get_value("Method", task.method, "method")
		if not method_path:
			frappe.logger().info(f"[Process Task] Skipping {task.name} - Method path not found in Method doctype")
			continue

		try:
			method_to_call = frappe.get_attr(method_path)
			enqueue(method_to_call, queue='default', timeout=600)
			frappe.logger().info(f"[Process Task] Ran {task.method} for {task.name}")
		except Exception as e:
			frappe.logger().error(f"[Process Task] Failed to run {task.method} for {task.name} - {e}")

def trigger_method_from_monthly_on_last_day_process_task():
	today = getdate()

	if today != get_last_day(today):
		return

	process_tasks = frappe.db.sql("""
			SELECT
				name, method, frequency, repeat_on_last_day, repeat_on_day
			FROM
				`tabProcess Task`
			WHERE
				is_active = 1 AND task_type = 'Routine' AND is_erp_task = 1 AND is_automated = 1
				AND frequency = 'Monthly' AND repeat_on_last_day = 1
				AND start_date <= %(today)s AND (end_date IS NULL OR end_date > %(today)s)
		""", {"today": today}, as_dict=True)

	for task in process_tasks:
		if not task.method:
			frappe.logger().info(f"[Process Task] Skipping {task.name} - No method defined")
			continue

		method_path = frappe.get_value("Method", task.method, "method")
		if not method_path:
			frappe.logger().info(f"[Process Task] Skipping {task.name} - Method path not found in Method doctype")
			continue

		try:
			method_to_call = frappe.get_attr(method_path)
			enqueue(method_to_call, queue='default', timeout=600)
			frappe.logger().info(f"[Process Task] Ran {task.method} for {task.name}")
		except Exception as e:
			frappe.logger().error(f"[Process Task] Failed to run {task.method} for {task.name} - {e}")

def get_second_weekday(year, month,dayname):
	c = calendar.Calendar(firstweekday=calendar.SUNDAY)
	monthcal = c.monthdatescalendar(year, month)
	weekday_index = list(calendar.day_name).index(dayname)
	# Find all matching weekdays in the given month
	weekdays = [day for week in monthcal for day in week
                if day.weekday() == weekday_index and day.month == month]
	# Return the second weekday
	return weekdays[1] if len(weekdays) >= 2 else None
