import frappe

from frappe.utils import today, add_days, date_diff



def process_contracts(contracts_list):
    for contract in contracts_list:
        contract_doc = frappe.get_doc('Contracts', contract)
        contract_doc.append('contract_date', {
            'contract_start_date': contract_doc.start_date,
            'contract_end_date': contract_doc.end_date
        })

        duration = date_diff(contract_doc.end_date, contract_doc.start_date)
        contract_doc.start_date = add_days(contract_doc.end_date, 1)
        contract_doc.end_date = add_days(contract_doc.end_date, duration + 1)

        contract_doc.save()

    frappe.db.commit()


def execute():
    filters = {
        'end_date': ["<=", today()],
        'is_auto_renewal': 1,
        'workflow_state': 'Active'
    }

    while True:
        contracts_list = frappe.db.get_list('Contracts', fields=["name"], filters=filters, order_by="start_date")
        
        if not contracts_list:
            break

        process_contracts(contracts_list)
