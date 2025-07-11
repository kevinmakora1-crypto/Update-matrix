import frappe

def execute():
    # Reload doctype so that newly added fields should be added first before executing patch
    frappe.reload_doctype("Operations Post")

    # Get all Operations Post records with a linked Project
    operations_posts = frappe.get_all("Operations Post", filters={"project": ["!=", ""]}, fields=["name", "project"])

    for op in operations_posts:
        target_contract = frappe.db.get_value("Contracts", { "project": op.project }, ["name", "start_date"], as_dict=True)

        if not target_contract:
            continue 

        # Try to fetch the first date from the dates child table of Contract
        child_start_date = frappe.get_all(
            "Contracts Date",
            filters={"parent": target_contract.name},
            fields=["contract_start_date"],
            order_by="idx asc",
            limit=1
        )

        if child_start_date:
            start_date = child_start_date[0].contract_start_date
        else:
            # Fallback to the contract start date
            start_date = target_contract.start_date

        if start_date:
            frappe.db.set_value("Operations Post", op.name, "start_date", start_date)

    frappe.db.commit()

