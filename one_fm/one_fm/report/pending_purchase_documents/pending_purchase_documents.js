frappe.query_reports["Pending Purchase Documents"] = {
    "filters": [
        {
            "fieldname": "request_for_material",
            "label": __("RFM"),
            "fieldtype": "Link",
            "options": "Request for Material",
            "reqd": 0,
        },
        {
            "fieldname": "one_fm_request_for_purchase",
            "label": __("RFP"),
            "fieldtype": "Link",
            "options": "Request for Purchase",
            "reqd": 0,
        },
        {
            "fieldname": "one_fm_request_for_purchase_status",
            "label": __("RFP Status"),
            "fieldtype": "Select",
            "options": "\nDraft\nDraft Request\nAccepted\nSubmitted\nCancelled\nApproved\nRejected",
            "reqd": 0,
        },
        {
            "fieldname": "purchase_order",
            "label": __("PO"),
            "fieldtype": "Link",
            "options": "Purchase Order",
            "reqd": 0,
        },
        {
            "fieldname": "purchase_order_status",
            "label": __("PO Status"),
            "fieldtype": "Select",
            "options": "\nDraft\nOn Hold\nTo Receive and Bill\nTo Bill\nTo Receive\nCompleted\nCancelled\nClosed\nDelivered",
            "reqd": 0,
        },
    ]
};

