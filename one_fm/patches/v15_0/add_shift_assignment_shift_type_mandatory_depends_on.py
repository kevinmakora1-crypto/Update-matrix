import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def execute():
    make_property_setter(
        doctype="Shift Assignment",
        fieldname="shift_type",
        property="mandatory_depends_on",
        value="eval:!doc.is_event_based_shift",
        property_type="Data",
        for_doctype=False,
        validate_fields_for_doctype=False
    )
    make_property_setter(
        doctype="Shift Assignment",
        fieldname="shift_type",
        property="reqd",
        value=0,
        property_type="Check",
        for_doctype=False,
        validate_fields_for_doctype=False
    )