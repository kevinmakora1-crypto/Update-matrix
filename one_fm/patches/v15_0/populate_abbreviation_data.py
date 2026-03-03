import frappe

def execute():
    # 1. Update Accommodation Space Type abbreviations
    type_abbreviations = {
        "Bedroom": "R",
        "Bathroom": "T",
        "Kitchen": "K",
        "Living room": "L",
        "Office": "O"
    }

    for space_type, abbreviation in type_abbreviations.items():
        if frappe.db.exists("Accommodation Space Type", space_type):
            frappe.db.set_value("Accommodation Space Type", space_type, "abbreviation", abbreviation)
            frappe.db.commit()

    # 2. Update Accommodation Space records
    # Fetch all Accommodation Space records that have a linked space type
    spaces = frappe.get_all("Accommodation Space", fields=["name", "accommodation_space_type"])
    
    for space in spaces:
        print(space.name)
        if space.accommodation_space_type:
            print(space.accommodation_space_type)
            # Get the abbreviation from the linked type
            abbreviation = frappe.db.get_value("Accommodation Space Type", space.accommodation_space_type, "abbreviation")
            print(abbreviation)
            if abbreviation:
                # Update the hidden field on Accommodation Space
                frappe.db.set_value("Accommodation Space", space.name, "space_type_abbreviation", abbreviation)
                frappe.db.commit()