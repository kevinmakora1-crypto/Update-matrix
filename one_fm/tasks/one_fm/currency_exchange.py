import frappe
from frappe.utils import today
from erpnext.setup.utils import get_exchange_rate

def update_currency_exchange_rates():
    """
    Fetches and creates currency exchange records for specified currency pairs
    if they don't already exist for the current date.
    """
    try:
        settings = frappe.get_doc("Currency Exchange Settings")
        service_provider = settings.service_provider
        business_currencies = [d.currency for d in settings.get("business_currencies", [])]
    except frappe.DoesNotExistError:
        frappe.log_error(
            title="Currency Exchange Settings Not Found",
            message="Please configure the Currency Exchange Settings doctype."
        )
        return

    if not service_provider:
        frappe.log_error(
            title="API Provider Not Set",
            message="Please set an API provider in Currency Exchange Settings."
        )
        return

    to_currency = "KWD"
    date = today()

    currency_pairs = []
    for currency in business_currencies:
        if currency != to_currency:
            currency_pairs.append((currency, to_currency))
            currency_pairs.append((to_currency, currency))

    try:
        for from_curr, to_curr in currency_pairs:
            if frappe.db.exists("Currency Exchange", {
                "date": date,
                "from_currency": from_curr,
                "to_currency": to_curr
            }):
                continue

            exchange_rate = get_exchange_rate(from_curr, to_curr, date)

            new_rate = frappe.new_doc("Currency Exchange")
            new_rate.date = date
            new_rate.from_currency = from_curr
            new_rate.to_currency = to_curr
            new_rate.exchange_rate = exchange_rate
            new_rate.insert(ignore_permissions=True)
        
        frappe.db.commit()

    except Exception:
        frappe.log_error(
            title="Currency Exchange Update Failed",
            message=frappe.get_traceback()
        )
