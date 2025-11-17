from frappe import _

from erpnext.accounts.doctype.purchase_invoice.purchase_invoice_dashboard import get_data as get_standard_data

def get_data(data=None, **kwargs):
    if not data:
        data = {}

    data = get_standard_data()

    data['non_standard_fieldnames'] = data.get('non_standard_fieldnames', {})
    data['non_standard_fieldnames']['Sales Invoice'] = 'custom_sales_invoice'
    
    data['internal_links'] = data.get('internal_links', {})
    data['internal_links']['Sales Invoice'] = 'custom_sales_invoice'
    
    reference_found = False
    for transaction in data.get('transactions', []):
        if transaction.get('label') == _('Reference'):
            if 'Sales Invoice' not in transaction['items']:
                transaction['items'].append('Sales Invoice')
            reference_found = True
            break

    if not reference_found:
        data['transactions'].append({
            'label': _('Reference'),
            'items': ['Sales Invoice']
        })
    
    return data