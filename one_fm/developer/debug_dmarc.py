import frappe
import parsedmarc

def execute():
	"""Debug: inspect parsedmarc output structure for date_range."""
	# Get one raw XML
	raw = frappe.db.sql("SELECT raw_xml FROM `tabDMARC Report` LIMIT 1", as_dict=True)
	if not raw or not raw[0].raw_xml:
		print("No raw XML found")
		return

	report = parsedmarc.parse_aggregate_report_xml(raw[0].raw_xml)

	meta = report.get("report_metadata", {}) if isinstance(report, dict) else getattr(report, "report_metadata", {})

	print(f"report type: {type(report)}")
	print(f"report keys: {list(report.keys()) if isinstance(report, dict) else dir(report)}")
	print(f"meta type: {type(meta)}")
	print(f"meta keys: {list(meta.keys()) if isinstance(meta, dict) else dir(meta)}")

	date_range = meta.get("date_range", None) if isinstance(meta, dict) else getattr(meta, "date_range", None)
	print(f"date_range type: {type(date_range)}")
	print(f"date_range value: {date_range}")

	if isinstance(date_range, dict):
		print(f"date_range keys: {list(date_range.keys())}")
		for k, v in date_range.items():
			print(f"  {k}: {v} (type: {type(v)})")
	elif date_range is not None:
		print(f"date_range attrs: {[a for a in dir(date_range) if not a.startswith('_')]}")
