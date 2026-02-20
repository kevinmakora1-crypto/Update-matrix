import frappe
from one_fm.custom.assignment_rule.assignment_rule import  get_assignment_rule_json_file, create_assignment_rule

def execute():
    frappe.delete_doc("Assignment Rule", "Attendance Check Reports To", ignore_missing=True)
    frappe.delete_doc("Assignment Rule", "Attendance Check Site Supervisor", ignore_missing=True)
    frappe.delete_doc("Assignment Rule", "Attendance Check Shift Supervisor", ignore_missing=True)
    create_assignment_rule(get_assignment_rule_json_file("action_attendance_check_approver.json"))
