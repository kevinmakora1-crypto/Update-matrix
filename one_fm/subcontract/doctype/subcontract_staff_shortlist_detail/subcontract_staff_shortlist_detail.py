# Copyright (c) 2023, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from one_fm.ocr_utils import (
	extract_kuwait_civil_id_data,
	validate_civil_id_number,
	compare_arabic_names
)
import os


class SubcontractStaffShortlistDetail(Document):
	def validate(self):
		"""Validate Civil ID number format and dates"""
		if self.id_type == "Civil ID" and self.civil_id_no:
			if not validate_civil_id_number(self.civil_id_no):
				frappe.throw(_("Civil ID No must be exactly 12 digits"))


@frappe.whitelist()
def trigger_ocr(docname, file_url):
	"""
	Trigger OCR processing for uploaded Civil ID document
	
	Args:
		docname (str): Name of the Subcontract Staff Shortlist Detail document
		file_url (str): URL of the uploaded file
		
	Returns:
		dict: Extracted data or error message
	"""
	try:
		# Get the document
		doc = frappe.get_doc("Subcontract Staff Shortlist Detail", docname)
		
		# Only process if ID Type is Civil ID
		if doc.id_type != "Civil ID":
			return {
				"success": False,
				"message": "OCR is only triggered for Civil ID type"
			}
		
		# Get file path from URL
		# Handle both /files/ and /private/files/ URLs
		if file_url.startswith('/files/'):
			# Public file
			file_path = frappe.get_site_path('public', 'files', file_url.split('/files/')[-1])
		elif file_url.startswith('/private/files/'):
			# Private file
			file_path = frappe.get_site_path('private', 'files', file_url.split('/private/files/')[-1])
		else:
			# Try to construct path from full URL
			file_path = frappe.get_site_path('public', file_url.lstrip('/'))
		
		if not os.path.exists(file_path):
			return {
				"success": False,
				"message": "File not found",
				"path": file_path,
				"url": file_url
			}
		
		# Extract data using OCR
		extracted_data = extract_kuwait_civil_id_data(file_path)
		
		# Validate extracted data
		if not extracted_data.get('civil_id_no'):
			return {
				"success": False,
				"message": "OCR failed to read the document clearly."
			}
		
		# Get parent document to check company name
		parent_doc = frappe.get_doc("Subcontract Staff Shortlist", doc.parent)
		
		# Check if subcontractor name in Arabic exists
		subcontractor_name_arabic = None
		if parent_doc.subcontractor:
			# Get from Supplier doctype
			subcontractor_name_arabic = frappe.db.get_value(
				"Supplier", 
				parent_doc.subcontractor, 
				"supplier_name_in_arabic"
			)
		
		# Prepare warnings
		warnings = []
		
		# Compare company names if both exist
		if extracted_data.get('company_name_arabic') and subcontractor_name_arabic:
			if not compare_arabic_names(extracted_data['company_name_arabic'], subcontractor_name_arabic):
				warnings.append("Subcontractor Name in Arabic not matching with the Staff Civil ID.")
		elif extracted_data.get('company_name_arabic') and not subcontractor_name_arabic:
			warnings.append("Comparison failed: Subcontractor Name in Arabic is missing in the main form. Please update the Subcontractor record first.")
		
		return {
			"success": True,
			"data": {
				"civil_id_no": extracted_data.get('civil_id_no'),
				"civil_id_expiry_date": extracted_data.get('expiry_date'),
				"date_of_birth": extracted_data.get('birth_date')
			},
			"warnings": warnings
		}
		
	except Exception as e:
		frappe.log_error(message=f"OCR Trigger Error: {str(e)}", title="Civil ID OCR")
		return {
			"success": False,
			"message": str(e)
		}
