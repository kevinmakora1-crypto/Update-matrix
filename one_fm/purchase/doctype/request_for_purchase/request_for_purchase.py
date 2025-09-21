# -*- coding: utf-8 -*-
# Copyright (c) 2020, ONE FM and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import nowdate, getdate, get_url, get_fullname
from one_fm.processor import sendemail
from frappe.utils.user import get_users_with_role
from frappe.permissions import has_permission
from one_fm.api.doc_events import get_employee_user_id
from frappe.desk.form.assign_to import add as add_assignment, DuplicateToDoError
from one_fm.utils import get_users_with_role_permitted_to_doctype

class RequestforPurchase(Document):
	def onload(self):
		self.set_onload('exists_qfs', False)
		if frappe.db.get_value('Quotation From Supplier', {'request_for_purchase': self.name}, 'name'):
			self.set_onload('exists_qfs', True)

	def on_submit(self):
		self.assign_purchase_officer()

	def assign_purchase_officer(self):
		purchase_officers = get_users_with_role_permitted_to_doctype('Purchase Officer', self.doctype)
		if purchase_officers:
			requested_items = '<br>'.join([i.item_name for i in self.items])
			add_assignment({
				'doctype': self.doctype,
				'name': self.name,
				'assign_to': purchase_officers,
				'description':
				_(
					f"""
						Please Note that a Request for Purchase {self.name} has been submitted.<br>
						Requested Items: {requested_items} <br>
						Please review and take necessary actions
					"""
				)
			})

	def validate_items_to_order(self):
		if not self.items_to_order:
			frappe.throw(_("Fill Items to Order!"))
		no_item_code_in_items_to_order = [item.idx for item in self.items_to_order if (not item.item_code or not item.supplier)]
		if no_item_code_in_items_to_order and len(no_item_code_in_items_to_order) > 0:
			frappe.throw(_("Set Item Code/Supplier in <b>Items to Order</b> rows {0}".format(no_item_code_in_items_to_order)))

		# Get items qty is greater than the requested qty
		items = [item.idx for item in self.items_to_order if (item.qty_requested and item.qty_requested < item.qty)]
		if items and len(items) > 0:
			frappe.throw(_("Items <b>Items Order</b> are greater in quantity than requested in rows {0}".format(items)))

	@frappe.whitelist()
	def make_purchase_order_for_quotation(self, warehouse=None):
		self.validate_items_to_order()
		if self.items_to_order:
			wh = warehouse if warehouse else self.warehouse
			for item in self.items_to_order:
				if item.t_warehouse:
					wh = item.t_warehouse
				create_purchase_order(supplier=item.supplier, request_for_purchase=self.name, item_code=item.item_code,
					qty=item.qty, rate=item.rate, delivery_date=item.delivery_date, uom=item.uom, description=item.description,
					warehouse=wh, quotation=item.quotation, do_not_submit=True)

	@frappe.whitelist()
	def notify_the_rfm_requester(self):
		rfm = frappe.get_doc('Request for Material', self.request_for_material)
		page_link = get_url(rfm.get_url())
		message = "Not able to fulfil the RFM <a href='{0}'>{1}</a>".format(page_link, rfm.name)
		message += "<br/> due to lack of availabilty of the item(s) listed below with the specification"
		message += "<ul>"
		for item in self.items:
			availabilty = False
			for items_to_order in self.items_to_order:
				if item.item_name == items_to_order.item_name:
					availabilty = True
			if not availabilty:
				message += "<li>" + item.item_name +"</li>"
		message += "</ul>"
		subject = "Not able to fulfil the RFM <a href='{0}'>{1}</a>".format(page_link, rfm.name)
		sendemail(recipients=[rfm.requested_by], subject=subject, message=message, reference_doctype=rfm.doctype, reference_name=rfm.name)
		create_notification_log(subject, message, [rfm.requested_by], rfm)
		self.db_set('notified_the_rfm_requester', True)
		frappe.msgprint(_("Notification sent to RFM Requester"))


	def before_cancel(self):
		if self.workflow_state == "Rejected":
			self.check_related_pos_before_cancel()

	def check_related_pos_before_cancel(self):
		approved_pos = frappe.db.get_list('Purchase Order', {
			'one_fm_request_for_purchase': self.name,
			'docstatus': 1,
			'workflow_state': 'Approved'
		}, ['name'])
		
		draft_pos = frappe.db.get_list('Purchase Order', {
			'one_fm_request_for_purchase': self.name,
			'docstatus': ['in', [0, 1]],
			'workflow_state': 'Draft'
		}, ['name'])
		
		pending_pos = frappe.db.get_list('Purchase Order', {
			'one_fm_request_for_purchase': self.name,
			'docstatus': ['in', [0, 1]],
			'workflow_state': ['in', ['Pending Purchase Manager', 'Pending Finance Approver']]
		}, ['name', 'workflow_state'])
		
		if approved_pos:
			if pending_pos:
				approved_list = ", ".join([po.name for po in approved_pos])
				other_list = ", ".join([po.name for po in pending_pos])
				frappe.throw(
					_("Please note that {0} has related Purchase Orders in different stages: {1} > Pending Approval, {2} > Approved. Cancellation of this RFP is not allowed while Approved POs exist. You must first cancel the Approved POs.").format(
						self.name, other_list, approved_list
					),
					title=_("Cancellation Blocked – Mixed Purchase Order Stages Found"),
					exc=frappe.ValidationError
				)
			else:
				po_list = ", ".join([po.name for po in approved_pos])
				frappe.throw(
					_("Please note that {0} has related Purchase Orders ({1}) in Approved stage. To proceed, you must first cancel these Purchase Orders. Cancellation of this RFP is not allowed until all related POs are cancelled.").format(
						self.name, po_list
					),
					title=_("RFP Cancellation blocked. Approved Purchase Order found."),
					exc=frappe.ValidationError
				)

		elif draft_pos and pending_pos:
			all_draft_pending = draft_pos + pending_pos
			self.delete_related_pos(all_draft_pending)

		elif draft_pos:
			self.delete_related_pos(draft_pos)

		elif pending_pos:
			self.delete_related_pos(pending_pos)

	def delete_related_pos(self, related_pos):
		for po in related_pos:
			try:
				po_doc = frappe.get_doc('Purchase Order', po.name)
				
				if po_doc.docstatus == 1:
					po_doc.cancel()
				
				frappe.delete_doc('Purchase Order', po.name, force=1)
				
			except Exception as e:
				frappe.log_error(f"Error deleting PO {po.name}: {str(e)}")
				frappe.throw(_("Error deleting Purchase Order {0}: {1}").format(po.name, str(e)))



@frappe.whitelist()
def check_related_pos_before_cancel(doc):
    doc_dict = json.loads(doc)
    
    approved_pos = frappe.db.get_list('Purchase Order', {
        'one_fm_request_for_purchase': doc_dict.get('name'),
        'docstatus': 1,
        'workflow_state': 'Approved'
    }, ['name'])
    
    draft_pos = frappe.db.get_list('Purchase Order', {
        'one_fm_request_for_purchase': doc_dict.get('name'),
        'docstatus': ['in', [0, 1]],
        'workflow_state': 'Draft'
    }, ['name'])
    
    pending_pos = frappe.db.get_list('Purchase Order', {
        'one_fm_request_for_purchase': doc_dict.get('name'),
        'docstatus': ['in', [0, 1]],
        'workflow_state': ['in', ['Pending Purchase Manager', 'Pending Finance Approver']]
    }, ['name', 'workflow_state'])
    
    if approved_pos:
        all_other_pos = draft_pos + pending_pos
        if all_other_pos:
            approved_list = ", ".join([po.name for po in approved_pos])
            other_list = ", ".join([po.name for po in all_other_pos])
            return {
                'error': True,
                'type': 'mixed',
                'title': 'Cancellation Blocked – Mixed Purchase Order Stages Found',
                'message': f"Please note that {doc_dict.get('name')} has related Purchase Orders in different stages: {other_list} > Pending Approval, {approved_list} > Approved. Cancellation of this RFP is not allowed while Approved POs exist. You must first cancel the Approved POs.",
                'approved_list': approved_list,
                'other_list': other_list
            }
        else:
            po_list = ", ".join([po.name for po in approved_pos])
            return {
                'error': True,
                'type': 'approved_only',
                'title': 'RFP Cancellation blocked. Approved Purchase Order found.',
                'message': f"Please note that {doc_dict.get('name')} has related Purchase Orders ({po_list}) in Approved stage. To proceed, you must first cancel these Purchase Orders. Cancellation of this RFP is not allowed until all related POs are cancelled.",
                'approved_list': po_list
            }
    elif draft_pos and pending_pos:
        all_draft_pending = draft_pos + pending_pos
        po_list = ", ".join([po.name for po in all_draft_pending])
        return {
            'error': True,
            'type': 'draft_pending_confirmation',
            'title': 'Purchase Order is in Pending Approval Stage',
            'message': f"Please note that {doc_dict.get('name')} has related Purchase Orders ({po_list}) currently in Pending Approval stage. Cancelling this RFP will automatically delete these Purchase Orders. Do you want to proceed?",
            'draft_pending_list': po_list
        }
    elif draft_pos:
        po_list = ", ".join([po.name for po in draft_pos])
        return {
            'error': True,
            'type': 'draft_confirmation',
            'title': 'Purchase Order is in Pending Approval Stage',
            'message': f"Please note that {doc_dict.get('name')} has related Purchase Orders ({po_list}) currently in Pending Approval stage. Cancelling this RFP will automatically delete these Purchase Orders. Do you want to proceed?",
            'draft_list': po_list
        }
    
    return {'error': False}


def create_notification_log(subject, message, for_users, reference_doc):
	if 'Administrator' in for_users:
		for_users.remove('Administrator')
	for user in for_users:
		doc = frappe.new_doc('Notification Log')
		doc.subject = subject
		doc.email_content = message
		doc.for_user = user
		doc.document_type = reference_doc.doctype
		doc.document_name = reference_doc.name
		doc.from_user = reference_doc.modified_by
		# If notification log type is Alert then it will not send email for the log
		doc.type = 'Alert'
		doc.insert(ignore_permissions=True)

@frappe.whitelist()
def make_request_for_quotation(source_name, target_doc=None):
	doclist = get_mapped_doc("Request for Purchase", source_name, 	{
		"Request for Purchase": {
			"doctype": "Request for Supplier Quotation",
			"field_map": [
				["name", "request_for_purchase"]
			],
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Request for Purchase Item": {
			"doctype": "Request for Supplier Quotation Item",
			"field_map": [
				["uom", "uom"]
			]
		}
	}, target_doc)

	return doclist

@frappe.whitelist()
def make_quotation_comparison_sheet(source_name, target_doc=None):
	doclist = get_mapped_doc("Request for Purchase", source_name, 	{
		"Request for Purchase": {
			"doctype": "Quotation Comparison Sheet",
			"field_map": [
				["name", "request_for_purchase"]
			],
			"validation": {
				"docstatus": ["=", 1]
			}
		}
	}, target_doc)
	rfq = frappe.db.get_value('Request for Supplier Quotation', {'request_for_purchase': doclist.request_for_purchase}, 'name')
	doclist.request_for_quotation = rfq if rfq else ''
	return doclist

def create_purchase_order(**args):
	args = frappe._dict(args)
	po_id = frappe.db.exists('Purchase Order',
		{'one_fm_request_for_purchase': args.request_for_purchase, 'docstatus': ['<', 2], 'supplier': args.supplier}
	)
	if po_id:
		po = frappe.get_doc('Purchase Order', po_id)
	else:
		po = frappe.new_doc("Purchase Order")
		po.transaction_date = nowdate()
		po.set_warehouse = args.warehouse
		po.quotation = args.quotation
		po.supplier = args.supplier
		po.is_subcontracted = args.is_subcontracted or "No"
		po.conversion_factor = args.conversion_factor or 1
		po.supplier_warehouse = args.supplier_warehouse or None
		po.one_fm_request_for_purchase = args.request_for_purchase
		po.is_subcontracted = False

	po.append("items", {
		"item_code": args.item_code,
		"item_name": args.item_name,
		"description": args.description,
		"uom": args.uom,
		"qty": args.qty,
		"rate": args.rate,
		"amount": args.qty * args.rate,
		"schedule_date": getdate(args.delivery_date) if (args.delivery_date and getdate(nowdate()) < getdate(args.delivery_date)) else getdate(nowdate()),
		"expected_delivery_date": args.delivery_date
	})
	if not args.do_not_save:
		po.save(ignore_permissions=True)
		if not args.do_not_submit:
			po.submit()
