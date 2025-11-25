import frappe

def execute():
    settings = frappe.get_single("Currency Exchange Settings")

    changed = False

    # Ensure service provider is set to Custom so api_endpoint is editable (read_only_depends_on logic)
    desired_service_provider = "Custom"
    if settings.get("service_provider") != desired_service_provider:
        settings.service_provider = desired_service_provider
        changed = True

    # Set / update api_endpoint
    desired_endpoint = "https://open.er-api.com/v6/latest/{from_currency}"
    if settings.get("api_endpoint") != desired_endpoint:
        settings.api_endpoint = desired_endpoint
        changed = True

    # Seed Business Currencies
    existing = {d.currency for d in settings.get("business_currencies", []) if getattr(d, "currency", None)}
    for curr in ["AED", "USD", "INR"]:
        if curr not in existing:
            row = settings.append("business_currencies", {})
            row.currency = curr
            changed = True

    if changed:
        settings.save(ignore_permissions=True)
        frappe.db.commit()
