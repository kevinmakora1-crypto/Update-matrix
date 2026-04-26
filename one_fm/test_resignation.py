import frappe
from one_fm.api.v1.resignation import create_resignation

def run():
    try:
        frappe.set_user("Administrator")
        res = create_resignation(
            employee_id="2503003KE199",
            data={
                "resignation_initiation_date": "2026-04-25",
                "relieving_date": "2026-05-25"
            }
        )
        print(f"SUCCESS: {res}")
        frappe.db.commit()
    except Exception as e:
        print(f"FAILED: {str(e)}")
        print(frappe.get_traceback())

run()
