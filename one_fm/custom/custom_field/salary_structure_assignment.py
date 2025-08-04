def get_salary_structure_assignment_custom_fields():
    return {
        "Salary Structure Assignment": [
            {
                "fieldname": "custom_payroll_type",
                "fieldtype": "Select",
                "label": "Payroll Type",
                "insert_after": "salary_structure",
                "options": "\nBasic\nOver-Time"
            },
            {
                "fieldname": "custom_salary_structure_assignment_details",
                "fieldtype": "Section Break",
                "label": "Salary Structure Assignment Details",
                "insert_after": "custom_payroll_type",
                "collapsible": 1
            },
            {
                "fieldname": "custom_salary_component_assignment_detail",
                "fieldtype": "Table",
                "label": "Salary Component Assignment Detail",
                "insert_after": "custom_salary_structure_assignment_details",
                "options": "Salary Component Assignment Detail"
            }
        ]
    }