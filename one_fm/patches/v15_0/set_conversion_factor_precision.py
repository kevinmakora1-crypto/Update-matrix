import frappe

def execute():
    property_setters = [
        {
            'doctype_or_field': 'DocField',
            'doc_type': 'UOM Conversion Detail',
            'field_name': 'conversion_factor',
            'property': 'precision',
            'value': '6',
            'property_type': 'Int'
        },
        {
            'doctype_or_field': 'DocField',
            'doc_type': 'Purchase Order Item',
            'field_name': 'conversion_factor',
            'property': 'precision',
            'value': '4',
            'property_type': 'Int'
        },
        {
            'doctype_or_field': 'DocField',
            'doc_type': 'Purchase Receipt Item',
            'field_name': 'conversion_factor',
            'property': 'precision',
            'value': '4',
            'property_type': 'Int'
        },
        {
            'doctype_or_field': 'DocField',
            'doc_type': 'Purchase Invoice Item',
            'field_name': 'conversion_factor',
            'property': 'precision',
            'value': '4',
            'property_type': 'Int'
        }
    ]
    
    for ps_data in property_setters:
        property_setter_name = f"{ps_data['doc_type']}-{ps_data['field_name']}-{ps_data['property']}"
        
        if frappe.db.exists('Property Setter', property_setter_name):
            doc = frappe.get_doc('Property Setter', property_setter_name)
            doc.value = ps_data['value']
            doc.save()
        else:
            doc = frappe.new_doc('Property Setter')
            doc.update({
                'name': property_setter_name,
                'doctype_or_field': ps_data['doctype_or_field'],
                'doc_type': ps_data['doc_type'],
                'field_name': ps_data['field_name'],
                'property': ps_data['property'],
                'value': ps_data['value'],
                'property_type': ps_data['property_type']
            })
            doc.insert()
        
        frappe.db.commit()