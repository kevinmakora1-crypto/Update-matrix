import frappe



def execute():
    frappe.db.sql(""" UPDATE `tabEmployee ID` SET nationality = 'Sudanese' WHERE nationality = 'Sudani' """)
    frappe.db.sql(""" UPDATE `tabAccommodation Checkin Checkout` SET nationality = 'Sudanese' WHERE nationality = 'Sudani' """)
    frappe.db.sql(""" UPDATE `tabBed` SET nationality = 'Sudanese' WHERE nationality = 'Sudani' """)
    frappe.db.sql(""" UPDATE `tabEmployee` SET one_fm_nationality = 'Sudanese' WHERE one_fm_nationality = 'Sudani' """)
    frappe.db.sql(""" DELETE FROM `tabNationality` WHERE name = 'Sudani' """)