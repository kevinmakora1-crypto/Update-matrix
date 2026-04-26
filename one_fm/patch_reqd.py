import frappe

def run():
    try:
        cf_name = "Interview Round-one_fm_nationality"
        if frappe.db.exists("Custom Field", cf_name):
            doc = frappe.get_doc("Custom Field", cf_name)
            doc.reqd = 1
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            print("Successfully REACTIVATED Mandatory flag for Nationality in DB!")
            
            frappe.clear_cache(doctype="Interview Round")
            print("Cleared doc cache for Interview Round")
        else:
            print("Custom Field missing from DB")
            
    except Exception as e:
        print(f"Failed: {e}")
