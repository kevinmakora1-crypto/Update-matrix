import frappe

def execute():
    # Get all Operations Post records with a linked Project
    operations_posts = frappe.get_all("Operations Post", filters={"project": ["!=", ""]}, fields=["name", "project"])

    for op in operations_posts:
        project = frappe.db.get_value(
            "Project",
            op.project,
            ["expected_start_date", "expected_end_date"],
            as_dict=True
        )

        if project:
            frappe.db.set_value("Operations Post", op.name, {
                "start_date": project.expected_start_date,
                "end_date": project.expected_end_date
            })

    frappe.db.commit()
