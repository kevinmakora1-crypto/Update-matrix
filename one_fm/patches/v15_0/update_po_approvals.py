import frappe,json
from frappe.utils import getdate,get_date_str




def get_purchase_orders(batch_size=10):
    """Get All purchase orders that have on approval dates for Purchase Officer and Purchase Manager"""
    workflow_states = ['Approved',"Pending Purchase Manager","Pending Finance Approver"]
    purchases_missing_manager_approval = frappe.get_all("Purchase Order",{'custom_purchase_manager_approval_date':['is','not set'],'workflow_state':['in',workflow_states]},page_length =batch_size)
    purchases_missing_officer_approval =frappe.get_all("Purchase Order",{'custom_purchase_officer_approval_date':['is','not set'],'workflow_state':['in',workflow_states]},page_length =batch_size)
    all_purchases = purchases_missing_manager_approval+purchases_missing_officer_approval
    purchases = list(set([i.name for i in all_purchases])) #remove duplicates
    
    if purchases:
        print(f"About to process {len(purchases)} purchase orders {','.join(purchases)} ")
        update_approval_data(purchases)
        frappe.db.commit()
        


def update_approval_data(purchase_orders):
    """
        Update the approval dates of the purchase order during workflow:
         the follow approval dates are required:
         - Approval by Purchase Officer
         - Approval by Purchase Manager
    Args:
        purchase_orders (list): List of Valid Purchase Order

   
    """
    
    try:
        count=1
        existing_versions = frappe.get_all("Version",{'docname':['in',purchase_orders],'data':['like','%workflow_state%']},['creation','data','docname'])
        if existing_versions:
            for each in existing_versions:
                version_data_dict = json.loads(each.data)
                version_workflow_state_changes = version_data_dict['changed']
                for one in version_workflow_state_changes:
                    if  one[2] in ["Pending Approver",'Pending Purchase Manager']: #Purchase Officer Approval
                        frappe.db.set_value("Purchase Order",each.get("docname"),'custom_purchase_officer_approval_date',each.get('creation'))
                    if 'Pending Finance Manager' == one[2]:  #Purchase Manager Approval
                        frappe.db.set_value("Purchase Order",each.get("docname"),'custom_purchase_manager_approval_date',each.get('creation'))
                print(f'Done {count} versions from {len(existing_versions)}')
                count+=1
            
    except: 
        frappe.log_error(title = "Error setting PO approval dates",message = frappe.get_traceback())
    