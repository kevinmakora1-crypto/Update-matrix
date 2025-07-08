import frappe

def execute():
    onboarding_id = "EMP-ONB-2025-00315"
    shift_value = "Carpark-360 Car Park-Day-1"

    if frappe.db.exists("Onboard Employee", onboarding_id):
        frappe.db.set_value("Onboard Employee", onboarding_id, "operations_shift", shift_value)
        frappe.db.commit()
    else:
        return
    duty_doc = frappe.db.get_value("Duty Commencement", {"onboard_employee": onboarding_id}, "name")
    if duty_doc:
        frappe.db.set_value("Duty Commencement", duty_doc, "operations_shift", shift_value)
        frappe.db.commit()
    else:
        return