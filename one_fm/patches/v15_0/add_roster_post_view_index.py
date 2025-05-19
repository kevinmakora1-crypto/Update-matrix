import frappe

def execute():
	if frappe.db.exists("DocType", "Operations Post"):
		frappe.db.add_index("Post Schedule", ["post", "date"], "post_schedule_post_date")

	if frappe.db.exists("DocType", "Post Schedule"):
		frappe.db.add_index("Operations Post", ["project", "site"], "operations_post_project_site")
