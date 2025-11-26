from frappe import _

def get_data(**kwargs):
    data = kwargs.get('data')

    if data and 'transactions' in data:
        new_items = ['Career History', 'Best Reference']
        transactions = data.get('transactions', [])
        if transactions:
            first_section = transactions[0]
            items = first_section.setdefault('items', [])
            for item in new_items:
                if item not in items:
                    items.append(item)

    return data