import frappe

def execute():
	erf_name = "ERF-2025-00057"
	new_designation = "Security Guard"

	if frappe.db.exists("ERF", erf_name):
		# Update ERF itself
		frappe.db.set_value("ERF", erf_name, "designation", new_designation)
		frappe.db.set_value("ERF", erf_name, "job_title", new_designation)

		# Update Job Opening
		job_openings = frappe.get_all("Job Opening", filters={"one_fm_erf": erf_name}, pluck="name")
		for jo in job_openings:
			frappe.db.set_value("Job Opening", jo, "designation", new_designation)

		# Update Job Applicant
		job_applicants = frappe.get_all("Job Applicant", filters={"one_fm_erf": erf_name}, pluck="name")
		for ja in job_applicants:
			frappe.db.set_value("Job Applicant", ja, "designation", new_designation)
			frappe.db.set_value("Job Applicant", ja, "one_fm_designation", new_designation)

			# Update linked Job Offer
			job_offers = frappe.get_all("Job Offer", filters={"job_applicant": ja}, pluck="name")
			for offer in job_offers:
				frappe.db.set_value("Job Offer", offer, "designation", new_designation)

