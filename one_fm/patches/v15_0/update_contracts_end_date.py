import frappe 
from frappe.utils import add_days, date_diff, now_datetime, getdate
from one_fm.operations.doctype.operations_post.operations_post import create_new_schedule_for_project 


def execute():
    lulu_contract_project_partial = [
        "Lulu Hypermarket Express - Kuwait City",
        "Lulu Hypermarket Egaila + Lulu Hypermarket Camp House",
        "Lulu Hypermarket Express - Terrace Mall",
        "Lulu Express - Warehouse Mall",
        "Lulu Fresh Market - Khairan"
    ]
    contracts_to_renew = []
    for title_partial in lulu_contract_project_partial:
        found_contracts = frappe.get_list(
            "Contracts",
            filters={"project": ["like", f"%{title_partial}%"]},
            fields=["name", "contract_name", "start_date","end_date"],
            limit=1
        )
        if found_contracts:
            contracts_to_renew.append(found_contracts[0])
        else:
            frappe.log_error(f"Contract matching '{title_partial}' not found.", "Contract Auto-Renew Error")

    if not contracts_to_renew:
        frappe.log_error("No matching contracts found to renew.", "Contract Auto-Renew")
        return
    renew_contract_check(contracts_to_renew)
    
    
def renew_contract_check(contracts):
    for contract in contracts:
        try:
            current_year = now_datetime().year
            end_date_obj = getdate(contract.end_date)
            if end_date_obj.year == current_year and end_date_obj < now_datetime().date():
                contract_doc = renew_contracts(contract)
                create_new_schedule_for_project(contract_doc.project)
            else:
                while end_date_obj.year < current_year:
                    contract_doc = renew_contracts(contract)
                    end_date_obj = getdate(contract_doc.end_date)
                if end_date_obj.year == current_year and end_date_obj < now_datetime().date():
                    contract_doc = renew_contracts(contract)
                    create_new_schedule_for_project(contract_doc.project)
        except Exception as e:
            frappe.log_error(f"Error: {e}", "Contract Auto-Renew Error")
            return False


def renew_contracts(contract):
    contract_doc = frappe.get_doc('Contracts', contract["name"])
    contract_date = contract_doc.append('contract_date', {})
    contract_date.contract_start_date = contract_doc.start_date
    contract_date.contract_end_date = contract_doc.end_date
    duration = date_diff(contract_doc.end_date, contract_doc.start_date)
    contract_doc.start_date = add_days(contract_doc.end_date, 1)
    contract_doc.end_date = add_days(contract_doc.end_date, duration + 1)
    contract_doc.save()
    frappe.db.commit()
    return contract_doc