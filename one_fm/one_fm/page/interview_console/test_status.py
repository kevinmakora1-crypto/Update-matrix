import sys
sys.path.append('../../..')
import frappe

frappe.init(site='restoredmaster')
frappe.connect()

docs = frappe.get_all('Job Applicant', filters={'applicant_name': ['like', '%Kumar%']}, fields=['name', 'applicant_name', 'status'])
for d in docs:
    doc = frappe.get_doc('Job Applicant', d.name)
    val_status = doc.get('status')
    val_custom = doc.get('one_fm_applicant_status')
    val_wf = doc.get('workflow_state')
    print(f"{d.applicant_name}: status='{val_status}', custom='{val_custom}', wf='{val_wf}'")
