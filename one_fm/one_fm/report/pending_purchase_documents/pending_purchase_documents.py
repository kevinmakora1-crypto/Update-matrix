import frappe
from frappe import _


def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    return columns, data

def get_columns():
    return [
        _("Request for Material") + ":Link/Request for Material:250",
        _("Request for Purchase") + ":Link/Request for Purchase:250",
        _("RFP Status") + "::200",
        _("Purchase Order Request") + ":Link/Purchase Order:250",
        _("PO Status") + "::200",
    ]

def get_data(filters=None):
    final_data = []
    grouped_data = get_pending_po(filters)
    for data in grouped_data:
        final_data.append([
			data.get('request_for_material'),
			data.get('one_fm_request_for_purchase'),
			data.get('one_fm_request_for_purchase_status'),
			data.get('purchase_order'),
			data.get('purchase_order_status'),
		])
    
    return final_data


def get_pending_po(filters):  
    purchase_orders_conditions={}  
    if filters:
        if filters.one_fm_request_for_purchase:
            purchase_orders_conditions["one_fm_request_for_purchase"] = filters.one_fm_request_for_purchase
        if filters.purchase_order:
            purchase_orders_conditions["name"] = filters.purchase_order
        if filters.purchase_order_status:
            purchase_orders_conditions["status"] = filters.purchase_order_status
            
    purchase_orders = frappe.get_all("Purchase Order", 
                                     filters=purchase_orders_conditions,
                                     fields=["name as purchase_order", "workflow_state as po_status", "one_fm_request_for_purchase"])
    result = []
    for po in purchase_orders:
        rfp_conditions = {"name": po.one_fm_request_for_purchase}
        if filters and filters.one_fm_request_for_purchase_status:
            rfp_conditions["status"] = filters.one_fm_request_for_purchase_status
        if filters and filters.request_for_material:
            rfp_conditions["request_for_material"] = filters.request_for_material
        rfps = frappe.get_all("Request for Purchase", 
                              filters=rfp_conditions, 
                              fields=["name", "workflow_state", "request_for_material"])
        if rfps:
            rfp = rfps[0]                    
            po_status_colored = get_status_colored(po.po_status)
            rfp_status_colored = get_status_colored(rfp.workflow_state)

            result.append({
                            "purchase_order": po.purchase_order,
                            "purchase_order_status": po_status_colored,
                            "one_fm_request_for_purchase": rfp.name,
                            "one_fm_request_for_purchase_status": rfp_status_colored,
                            "request_for_material": rfp.request_for_material if rfp else None
                        })

    return result

def get_status_colored(status):
    status_colors = {
        "Draft": "red",
        "Pending Finance Approver": "gray",
        "Submit to Purchase Officer":"gray",
        "Approved": "green",
        "Rejected": "red",
        "Hold":"gray",
    }
    color_class = {
        "red": "red",
        "gray": "gray",
        "green": "green",
        "black": "darkgray",
    }.get(status_colors.get(status, "black"), "darkgray")

    return f'''
    <span class="indicator-pill {color_class} filterable no-indicator-dot ellipsis"
          data-filter="workflow_state,=,{status}" title="{status}">
        <span class="ellipsis">{status}</span>
    </span>
    '''
    