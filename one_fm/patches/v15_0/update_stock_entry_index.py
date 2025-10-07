import frappe

def execute():
    try:
        frappe.db.sql("ALTER TABLE `tabStock Ledger Entry` ADD INDEX `item_warehouse` (`item_code`, `warehouse`)")
        frappe.db.commit()
    except Exception as e:
        if "Duplicate key name" in str(e):
            pass
        else:
            raise