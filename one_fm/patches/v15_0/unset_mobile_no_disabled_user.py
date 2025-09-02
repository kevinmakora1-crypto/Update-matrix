import frappe

def execute():
    """
    Patch to unset mobile_no for all disabled users except Administrator.
    This runs only once and performs a silent update.
    Excludes users where mobile_no is None or empty string.
    """
    # Use a single SQL update for efficiency
    frappe.db.sql(
        """
        UPDATE `tabUser`
        SET mobile_no = NULL
        WHERE enabled = 0
        AND name != 'Administrator'
        AND (mobile_no IS NOT NULL AND mobile_no != '')
        """
    )
