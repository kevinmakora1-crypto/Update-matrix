from frappe import _

from erpnext.accounts.doctype.sales_invoice.sales_invoice_dashboard import get_data as get_standard_data

def get_data(data=None):
    if not data:
        data = {}

    data = get_standard_data()
    
    data['internal_links'] = data.get('internal_links', {})
    data['internal_links']['Purchase Invoice'] = ['items', 'custom_purchase_invoice']
    
    for transaction in data.get('transactions', []):
        if transaction.get('label') == _('Internal Transfers'):
            items = transaction.get('items', [])
            if 'Purchase Invoice' in items:
                items.remove('Purchase Invoice')
            break
    

    reference_found = False
    for transaction in data.get('transactions', []):
        if transaction.get('label') == _('Reference'):
            items = transaction.get('items', [])
            if 'Purchase Invoice' not in items:
                items.append('Purchase Invoice')
            reference_found = True
            break
    
    if not reference_found:
        data['transactions'].append({
            'label': _('Reference'),
            'items': ['Purchase Invoice']
        })
    
    return data