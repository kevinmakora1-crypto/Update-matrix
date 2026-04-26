import frappe
import imaplib
import email
import gzip
import zipfile
import io
import parsedmarc
from frappe.utils import get_datetime, now_datetime, from_timestamp

@frappe.whitelist()
def fetch_and_process_dmarc_reports():
	"""
	Fetches DMARC aggregate reports using settings from ONEFM General Setting,
	parses them using parsedmarc, and creates DMARC Report records.
	"""
	try:
		settings = frappe.get_single("ONEFM General Setting")
		
		if not settings.email_account or not settings.email_password:
			return "DMARC email credentials are not configured in ONEFM General Setting."

		# Get credentials
		imap_host = settings.imap_host or "imap.gmail.com"
		imap_port = settings.imap_port or 993
		username = settings.email_account
		password = settings.get_password("email_password")
		
		# Connect to IMAP
		mail = imaplib.IMAP4_SSL(imap_host, int(imap_port))
		mail.login(username, password)
		
		# Select Inbox
		mail.select("INBOX")
		
		# Search for emails from the last 7 days to ensure we don't miss any
		from datetime import datetime, timedelta
		date_str = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
		
		result, data = mail.search(None, f'(SINCE "{date_str}")')
		
		if result != "OK":
			return "Failed to search emails."

		msg_ids = data[0].split()
		processed_count = 0
		
		for num in reversed(msg_ids):
			result, msg_data = mail.fetch(num, '(RFC822)')
			if result != "OK":
				continue
				
			raw_email = msg_data[0][1]
			msg = email.message_from_bytes(raw_email)
			subject = msg.get("Subject", "")
			subject_lower = subject.lower()
			
			# Filter by subject keywords
			if "report" not in subject_lower and "dmarc" not in subject_lower:
				continue
				
			# Process attachments
			for part in msg.walk():
				if part.get_content_maintype() == "multipart":
					continue
				if part.get("Content-Disposition") is None:
					continue
					
				filename = part.get_filename()
				if filename and (filename.endswith(".gz") or filename.endswith(".zip")):
					payload = part.get_payload(decode=True)
					xml_content = None
					
					if filename.endswith(".gz"):
						try:
							xml_content = gzip.decompress(payload).decode("utf-8")
						except Exception:
							continue
					elif filename.endswith(".zip"):
						try:
							with zipfile.ZipFile(io.BytesIO(payload)) as z:
								for z_name in z.namelist():
									if z_name.endswith(".xml"):
										xml_content = z.read(z_name).decode("utf-8")
										break
						except Exception:
							continue
					
					if xml_content:
						if process_xml_report(xml_content):
							processed_count += 1

		mail.logout()
		
		# Update last fetch time
		settings.db_set("last_fetch_time", now_datetime())
		
		return f"Processed {processed_count} DMARC reports."

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "DMARC Processor Error")
		return {"error": str(e)}

def process_xml_report(xml_content):
	"""
	Parses the XML content and creates DMARC Report records.
	"""
	try:
		# Use parsedmarc to parse the XML
		report = parsedmarc.parse_aggregate_report_xml(xml_content)
		
		# Helper for both dict and object access
		def get_val(obj, key, default=None):
			if isinstance(obj, dict):
				return obj.get(key, default)
			return getattr(obj, key, default)

		report_meta = get_val(report, "report_metadata", {})
		report_id = get_val(report_meta, "report_id")
		
		if not report_id:
			return False
			
		# Deduplication based on report_id (fast check)
		if frappe.db.exists("DMARC Report", {"report_id": report_id}):
			return False
			
		policy_pub = get_val(report, "policy_published", {})
		
		# Create DMARC Report
		doc = frappe.new_doc("DMARC Report")
		doc.report_id = report_id
		doc.org_name = get_val(report_meta, "org_name")
		doc.org_email = get_val(report_meta, "email")
		doc.domain = get_val(policy_pub, "domain")
		
		# Dates (Handle Unix timestamps correctly)
		date_range = get_val(report_meta, "date_range", {})
		begin_ts = get_val(date_range, "begin")
		end_ts = get_val(date_range, "end")
		
		if begin_ts:
			doc.begin_date = from_timestamp(begin_ts)
		if end_ts:
			doc.end_date = from_timestamp(end_ts)
			
		doc.published_policy = get_val(policy_pub, "p")
		doc.published_spf_alignment = get_val(policy_pub, "aspf")
		doc.published_dkim_alignment = get_val(policy_pub, "adkim")
		doc.published_pct = get_val(policy_pub, "pct")
		doc.raw_xml = xml_content
		doc.status = "Processed"
		
		# Process Records
		total_msgs = 0
		total_pass = 0
		total_fail = 0
		
		records = get_val(report, "records", [])
		for r in records:
			row = doc.append("records", {})
			
			source = get_val(r, "source", {})
			alignment = get_val(r, "alignment", {})
			policy_eval = get_val(r, "policy_evaluated", {})
			identifiers = get_val(r, "identifiers", {})
			
			row.source_ip = get_val(source, "ip_address")
			row.source_country = get_val(source, "country")
			row.source_reverse_dns = get_val(source, "reverse_dns")
			row.source_base_domain = get_val(source, "base_domain")
			
			row.message_count = get_val(r, "count", 0)
			row.disposition = get_val(policy_eval, "disposition")
			
			row.dkim_aligned = 1 if get_val(alignment, "dkim") else 0
			row.spf_aligned = 1 if get_val(alignment, "spf") else 0
			row.dmarc_aligned = 1 if get_val(alignment, "dmarc") else 0
			
			row.dkim_result = get_val(policy_eval, "dkim")
			row.spf_result = get_val(policy_eval, "spf")
			
			row.header_from = get_val(identifiers, "header_from")
			row.envelope_from = get_val(identifiers, "envelope_from")
			
			overrides = get_val(policy_eval, "policy_override_reasons", [])
			if overrides:
				row.policy_override_reasons = ", ".join(overrides)
			
			total_msgs += row.message_count
			if row.dmarc_aligned:
				total_pass += row.message_count
			else:
				total_fail += row.message_count
				
		doc.total_messages = total_msgs
		doc.total_pass = total_pass
		doc.total_fail = total_fail
		if total_msgs > 0:
			doc.pass_rate = (total_pass / total_msgs) * 100
			
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		return True
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "DMARC XML Parsing Error")
		return False
