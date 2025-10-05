import frappe
from one_fm.setup.workflow import create_workflows


def execute():
    frappe.db.sql("""
        UPDATE `tabRole`
        SET role_name = "Government Relations Operator",
            name = "Government Relations Operator"
        WHERE name = "GRD Operator"
    """)
    
    frappe.db.sql("""
        UPDATE `tabHas Role`
        SET role = "Government Relations Operator"
        WHERE role = "GRD Operator"
    """)
    
    frappe.db.sql("""
        UPDATE `tabCustom DocPerm`
        SET role = "Government Relations Operator"
        WHERE role = "GRD Operator"
    """)

    create_workflows()