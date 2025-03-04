import frappe
from frappe import _

from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder

def validate_purchase_uom(doc, method):
    for item in doc.items:
        query = """
            select
                uom
            from
                `tabUOM Conversion Detail`
            where
                parent = %s
        """
        uoms_list = frappe.db.sql(
            query,
            item.item_code,
            as_list=True,
        )
        uoms = [item for sublist in uoms_list for item in sublist]
        if uoms and len(uoms) > 0:
            if item.uom not in uoms:
                msg = "The selected UOM in the row {0} is not having any UOM conversion Details in the item {1}".format(item.idx, item.item_code)
                frappe.throw(_(msg))

@frappe.whitelist()
def filter_purchase_uoms(doctype, txt, searchfield, start, page_len, filters):
    # filter UOM in item lines by UOM Conversion Detail set in the item
	query = """
		select
            uom
        from
            `tabUOM Conversion Detail`
        where
            parent = %(item_code)s
			and uom like %(txt)s
			limit %(start)s, %(page_len)s"""
	return frappe.db.sql(query,
		{
			'item_code': filters.get("item_code"),
			'start': start,
			'page_len': page_len,
			'txt': "%%%s%%" % txt
		}
	)



class PurchaseOrderOverride(PurchaseOrder):  

    def on_submit(self):
        self.update_rfp()

    def on_update_after_submit(self):
        self.update_rfp_after_submit()

    def on_cancel(self):
        self.update_rfp(is_cancel=True)

    def update_rfp(self, is_cancel: bool = False):
        if self.one_fm_request_for_purchase:
            for obj in self.items:
                purchased_quantity = frappe.db.get_value(
                    "Request for Purchase Item",
                    {
                        "parent": self.one_fm_request_for_purchase,
                        "parentfield": "items",
                        "parenttype": "Request for Purchase",
                        "item_code": obj.item_code,
                    },
                    "purchased_quantity"
                ) or 0 
                new_qty = (purchased_quantity - obj.qty) if is_cancel else (purchased_quantity + obj.qty)
                self.update_purchased_qty(new_qty=new_qty, rfp=self.one_fm_request_for_purchase, item_code=obj.item_code)



    def update_rfp_after_submit(self):
        if self.one_fm_request_for_purchase:
            purchase_orders = frappe.db.get_list("Purchase Order", filters={"one_fm_request_for_purchase": self.one_fm_request_for_purchase,"name": ["not in", [self.name]]}, pluck='name')
            for obj in self.items:
                item_qty = frappe.db.get_list("Purchase Order Item", {"parent": ["IN", purchase_orders], "item_code": obj.item_code, 
                                                                      'parentfield': 'items',}, pluck="qty")
                self.update_purchased_qty(new_qty=sum(item_qty), rfp=self.one_fm_request_for_purchase, item_code=obj.item_code)


    @staticmethod
    def update_purchased_qty(new_qty: int, rfp: str, item_code:str):
        frappe.db.sql(
            """
            UPDATE `tabRequest for Purchase Item`
            SET purchased_quantity = %s
            WHERE parenttype = 'Request for Purchase'
            AND parent = %s
            AND item_code = %s
            """,
            (new_qty, rfp, item_code),
        )
                