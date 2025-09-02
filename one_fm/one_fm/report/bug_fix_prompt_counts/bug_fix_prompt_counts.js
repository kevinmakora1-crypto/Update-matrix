// Copyright (c) 2024, ONE FM and contributors
// For license information, please see license.txt

frappe.query_reports["Bug Fix Prompt Counts"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "fieldtype": "Date",
            "label": "From Date",
            "reqd": 1,
            "default": frappe.datetime.add_days(frappe.datetime.now_date(), -6)
        },
        {
            "fieldname": "to_date",
            "fieldtype": "Date",
            "label": "To Date",
            "reqd": 1,
            "default": frappe.datetime.now_date()
        },
    ]
};
