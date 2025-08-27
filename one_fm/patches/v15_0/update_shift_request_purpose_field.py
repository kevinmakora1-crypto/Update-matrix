from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	create_custom_fields({
		"Shift Request": [
			{
				"fieldname": "purpose",
                "fieldtype": "Select",
                "label": "Purpose",
                "insert_after": "employee_name",
                "options": " \nAssign Day Off\nAssign Client Day Off\nAssign Unrostered Employee\nReplace Existing Assignment\nUpdate Existing Assignment\nDay Off Overtime",
                "reqd": 1,
                "translatable": 1
			},
		]
	})