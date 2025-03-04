import frappe

def execute():
    frappe.db.sql("""
        UPDATE `tabEmployee` em
        JOIN `tabOnboard Employee` oe ON oe.employee = em.name
        SET em.one_fm_provide_accommodation_by_company = 1
        WHERE oe.provide_accommodation_by_company = 1 
        AND em.one_fm_provide_accommodation_by_company = 0
    """)

 
    employees = frappe.get_all(
        "Employee",
        filters={"current_address": "", "one_fm_provide_accommodation_by_company": 1, "status": ["IN", ["Active", "Vacation"]]},
        pluck="name"
    )

    if not employees:
        return 
    
    employee_accommodations = frappe.db.sql("""
        SELECT acc.employee, a.accommodation
        FROM `tabAccommodation Checkin Checkout` acc
        JOIN `tabAccommodation` a ON a.name = acc.accommodation
        WHERE acc.type = 'IN'
        AND acc.employee IN %(employees)s
        AND acc.creation = (
            SELECT MAX(sub_acc.creation)
            FROM `tabAccommodation Checkin Checkout` sub_acc
            WHERE sub_acc.employee = acc.employee 
            AND sub_acc.type = 'IN'
        )
    """, {"employees": tuple(employees)}, as_dict=True)


    update_mappings = {record["employee"]: record["accommodation"] for record in employee_accommodations}


    for employee, accommodation in update_mappings.items():
        frappe.db.set_value("Employee", employee, "current_address", accommodation)
