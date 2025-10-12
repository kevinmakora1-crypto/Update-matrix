import frappe
from frappe import _

from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry

@frappe.whitelist()
def get_store_keeper_warehouses(user=frappe.session.user):
    '''
        Method to get list of warehouse in which the employee linked to the user set as Store Keeper
        args:
            user: user_id
    '''
    # Get employee linked to the user
    employee = frappe.db.exists("Employee", {"user_id": user})
    if employee:
        # Get all warehouse in which the employee set as store keeper
        warehouses = frappe.db.get_list("Warehouse", {"one_fm_store_keeper": employee})
        return [warehouse.name for warehouse in warehouses]
    return []


def alert_item_multiple_entry(doc, method):
    '''
        Method to alert the user about mutliple entry of same item code in Stock Entry
        args:
            doc: Object of Stock Entry
    '''
    # Prepare item code list
    items = []
    for item in doc.items:
        items.append(item.item_code)

    # Check if lenght of items code list not equal to lenght of set of item code
    if items and len(items) != len(set(items)):
        '''
            The List will have all occurances of item code we have in the item lines,
            the Set will have only one occurance of an item code.
        '''
        frappe.msgprint(_("Same item entered multiple times."), alert=True, indicator="orange")


class StockEntryOverride(StockEntry):

    def validate(self):
        super().validate()
        if self.docstatus == 0:
            self.update_rfm_quantities(use_current_doc=True)

    def on_submit(self):
        super().on_submit()
        self.update_rfm_quantities(use_current_doc=False)

    def on_cancel(self):
        super().on_cancel()
        self.update_rfm_quantities(use_current_doc=False)

    def update_rfm_quantities(self, use_current_doc=False):
        if not self.one_fm_request_for_material:
            return
        
        rfm = frappe.get_doc("Request for Material", self.one_fm_request_for_material)
        
        if rfm.purpose not in ["Transfer", "Issue"]:
            return
        total_transferred_issued = []
        total_pending = 0
        for rfm_item in rfm.items:
            total_transferred = 0
            total_issued = 0
            total_pending = 0
            
            if use_current_doc:
                stock_entries = frappe.db.sql("""
                    SELECT se.name, se.docstatus, se.stock_entry_type, sei.qty
                    FROM `tabStock Entry` se
                    INNER JOIN `tabStock Entry Detail` sei ON sei.parent = se.name
                    WHERE se.one_fm_request_for_material = %s
                    AND sei.item_code = %s
                    AND sei.s_warehouse = %s
                    AND se.docstatus IN (0, 1)
                    AND se.name != %s
                """, (rfm.name, rfm_item.item_code, rfm_item.warehouse, self.name), as_dict=1)
            else:
                stock_entries = frappe.db.sql("""
                    SELECT se.name, se.docstatus, se.stock_entry_type, sei.qty
                    FROM `tabStock Entry` se
                    INNER JOIN `tabStock Entry Detail` sei ON sei.parent = se.name
                    WHERE se.one_fm_request_for_material = %s
                    AND sei.item_code = %s
                    AND sei.s_warehouse = %s
                    AND se.docstatus IN (0, 1)
                """, (rfm.name, rfm_item.item_code, rfm_item.warehouse), as_dict=1)
            
            for se in stock_entries:
                if se.docstatus == 1:
                    if se.stock_entry_type == "Material Issue":
                        total_issued += se.qty
                    elif se.stock_entry_type in ["Material Transfer", "Material Transfer-In Transit"]:
                        total_transferred += se.qty
                elif se.docstatus == 0:
                    total_pending += se.qty
            
            if use_current_doc:
                for item in self.items:
                    if item.item_code == rfm_item.item_code and item.s_warehouse == rfm_item.warehouse:
                        if self.docstatus == 0:
                            total_pending += item.qty
                        break

            if rfm.purpose == "Transfer":
                total_transferred_issued.append(total_transferred)
                rfm_item.transferred_quantity = total_transferred
                rfm_item.custom_pending_quantity = total_pending
                rfm_item.quantity_to_transfer = rfm_item.qty - total_transferred - total_pending

            elif rfm.purpose == "Issue":
                
                total_transferred_issued.append(total_issued)
                rfm_item.issued_quantity = total_issued
                rfm_item.custom_pending_quantity = total_pending
                rfm_item.quantity_to_transfer = rfm_item.qty - total_issued - total_pending
        
        
        rfm.flags.ignore_permissions = True
        rfm.flags.ignore_validate_update_after_submit = True
        rfm.save()
        set_rfm_status(rfm,total_transferred_issued)
        
def set_rfm_status(rfm_doc,stock_details):
    total_items_issued_transferred = sum(stock_details)
    total_items_in_rfm = sum([item.qty for item in rfm_doc.items])
    if rfm_doc.purpose == "Transfer":
        if not total_items_issued_transferred:
            frappe.db.set_value(rfm_doc.doctype,rfm_doc.name, 'status', 'Pending')
        elif total_items_issued_transferred ==  total_items_in_rfm:
            frappe.db.set_value(rfm_doc.doctype,rfm_doc.name, 'status', 'Transferred')
        if total_items_issued_transferred:
            if  total_items_issued_transferred <  total_items_in_rfm:
                frappe.db.set_value(rfm_doc.doctype,rfm_doc.name, 'status', "Partially Transferred")
    elif rfm_doc.purpose == "Issue":
        if not total_items_issued_transferred:
            frappe.db.set_value(rfm_doc.doctype,rfm_doc.name, 'status', 'Pending')
        elif total_items_issued_transferred ==  total_items_in_rfm:
            frappe.db.set_value(rfm_doc.doctype,rfm_doc.name, 'status', 'Issued')
        if total_items_issued_transferred:
            if  total_items_issued_transferred <  total_items_in_rfm:
                frappe.db.set_value(rfm_doc.doctype,rfm_doc.name, 'status', "Partially Issued")
    
       