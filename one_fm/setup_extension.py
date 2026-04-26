import frappe

def execute():
    # 1. Create Child Table `Employee Resignation Extension Item`
    if not frappe.db.exists("DocType", "Employee Resignation Extension Item"):
        child_doc = frappe.copy_doc(frappe.get_doc("DocType", "Employee Resignation Withdrawal Item"))
        child_doc.name = "Employee Resignation Extension Item"
        child_doc.custom = 0
        child_doc.module = "one_fm"
        
        for df in child_doc.fields:
            if df.fieldname == "withdrawal_letter" or df.label == "Withdrawal Letter":
                df.fieldname = "extension_letter"
                df.label = "Extension Proof / Request Letter"
            elif df.fieldname == "withdrawal_status":
                df.fieldname = "extension_status"
                df.label = "Extension Status"
                
        child_doc.insert(ignore_permissions=True)
        print("Created Child DocType: Employee Resignation Extension Item")

    # 2. Create Parent Table `Employee Resignation Extension`
    if not frappe.db.exists("DocType", "Employee Resignation Extension"):
        parent_doc = frappe.copy_doc(frappe.get_doc("DocType", "Employee Resignation Withdrawal"))
        parent_doc.name = "Employee Resignation Extension"
        parent_doc.custom = 0
        parent_doc.module = "one_fm"
        
        new_ext_field = frappe.new_doc("DocField")
        new_ext_field.update({
            "fieldname": "extended_relieving_date",
            "label": "Extended Relieving Date",
            "fieldtype": "Date",
            "reqd": 1,
            "insert_after": "current_relieving_date"
        })
        
        for df in parent_doc.fields:
            if df.fieldname == "date_of_joining":
                df.fieldname = "current_relieving_date"
                df.label = "Current Relieving Date"
                df.fieldtype = "Date"
                df.read_only = 1
                df.default = None
            elif df.fieldname == "employees":
                df.options = "Employee Resignation Extension Item"
        
        parent_doc.append("fields", new_ext_field)
        
        # We must filter out "under_company_residency" properly without breaking prototypes
        fields = [f for f in parent_doc.fields if f.fieldname != "under_company_residency"]
        parent_doc.fields = fields
        
        parent_doc.insert(ignore_permissions=True)
        print("Created Parent DocType: Employee Resignation Extension")
    
    frappe.db.commit()

