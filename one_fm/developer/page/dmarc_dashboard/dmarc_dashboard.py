import frappe
from frappe.utils import flt, getdate, add_days, today

@frappe.whitelist()
def get_dashboard_data():
	"""
	Fetches all data required for the DMARC Dashboard.
	"""
	data = {}
	
	try:
		# 1. Summary Cards
		reports = frappe.get_all("DMARC Report", fields=["total_messages", "total_pass", "total_fail", "pass_rate", "org_name", "begin_date"])
		
		data["total_reports"] = len(reports)
		data["total_messages"] = sum(r.total_messages for r in reports)
		data["spoofing_attempts"] = sum(r.total_fail for r in reports)
		
		if data["total_reports"] > 0:
			data["pass_rate"] = sum(r.pass_rate for r in reports) / data["total_reports"]
		else:
			data["pass_rate"] = 0
			
		# 2. Daily Email Volume (Pass vs Fail over time)
		daily_data = {}
		for r in reports:
			date_str = str(getdate(r.begin_date))
			if date_str not in daily_data:
				daily_data[date_str] = {"pass": 0, "fail": 0}
			daily_data[date_str]["pass"] += r.total_pass
			daily_data[date_str]["fail"] += r.total_fail
			
		sorted_dates = sorted(daily_data.keys())
		data["daily_volume"] = {
			"labels": sorted_dates,
			"datasets": [
				{"name": "Pass", "values": [daily_data[d]["pass"] for d in sorted_dates]},
				{"name": "Fail", "values": [daily_data[d]["fail"] for d in sorted_dates]}
			]
		}
		
		# 3. Top 10 Source IPs
		top_ips = frappe.db.sql("""
			SELECT source_ip, SUM(message_count) as total_count
			FROM `tabDMARC Record`
			GROUP BY source_ip
			ORDER BY total_count DESC
			LIMIT 10
		""", as_dict=True)
		
		data["top_ips"] = {
			"labels": [r.source_ip for r in top_ips],
			"datasets": [{"values": [r.total_count for r in top_ips]}]
		}
		
		# 4. Pass/Fail Breakdown
		total_pass = sum(r.total_pass for r in reports)
		total_fail = sum(r.total_fail for r in reports)
		data["breakdown"] = {
			"labels": ["Pass", "Fail"],
			"datasets": [{"values": [total_pass, total_fail]}]
		}
		
		# 5. Reports by Org
		org_counts = {}
		for r in reports:
			org_counts[r.org_name] = org_counts.get(r.org_name, 0) + 1
			
		sorted_orgs = sorted(org_counts.items(), key=lambda x: x[1], reverse=True)[:10]
		data["org_reports"] = {
			"labels": [o[0] for o in sorted_orgs],
			"datasets": [{"values": [o[1] for o in sorted_orgs]}]
		}
		
		# 6. Spoofing Alert Table
		alerts = frappe.get_all("DMARC Record",
			filters={"dmarc_aligned": 0},
			fields=["parent", "source_ip", "source_country", "source_reverse_dns", "message_count", "disposition"],
			order_by="message_count desc",
			limit=20
		)
		
		report_dates = {r.name: r.begin_date for r in frappe.get_all("DMARC Report", fields=["name", "begin_date"])}
		for a in alerts:
			a["date"] = report_dates.get(a.parent)
			
		data["alerts"] = alerts
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Dashboard Data Error")
		return {"error": str(e)}
	
	return data
