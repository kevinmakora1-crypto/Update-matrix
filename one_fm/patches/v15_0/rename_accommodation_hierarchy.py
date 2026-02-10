import frappe
from one_fm.accommodation.doctype.accommodation_unit.accommodation_unit import get_next_unit_number
from one_fm.accommodation.doctype.accommodation_space.accommodation_space import get_next_space_number
from one_fm.accommodation.doctype.bed.bed import get_next_bed_number

def execute():
    # 1. Rename Accommodation
    frappe.reload_doc("accommodation", "doctype", "accommodation")
    rename_accommodation_records()

    # 2. Rename Accommodation Unit
    frappe.reload_doc("accommodation", "doctype", "accommodation_unit")
    rename_accommodation_unit_records()

    # 3. Rename Accommodation Space
    frappe.reload_doc("accommodation", "doctype", "accommodation_space")
    rename_accommodation_space_records()

    # 4. Rename Bed
    frappe.reload_doc("accommodation", "doctype", "bed")
    rename_bed_records()

    # 5. Update Naming Series
    update_naming_series()

def rename_accommodation_records():
    accommodations = frappe.get_all("Accommodation", fields=["name"])
    for acc in accommodations:
        old_name = acc.name
        # Skip if already renamed
        if old_name.startswith("ACC-"):
            continue
            
        new_name = f"ACC-{old_name}"
        
        try:
            frappe.rename_doc("Accommodation", old_name, new_name, force=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Failed to rename Accommodation {old_name}: {str(e)}", "Accommodation Migration Error")

def rename_accommodation_unit_records():
    # Order by creation to maintain sequence roughly
    units = frappe.get_all("Accommodation Unit", fields=["name", "accommodation", "floor", "floor_name"], order_by="creation asc")
    
    # We need to reset counters or just rely on get_next_unit_number if we process sequentially?
    # get_next_unit_number checks existing records in DB.
    # If we rename sequentialy, the new names are in DB, so get_next_unit_number will find them and increment.
    # So we can just process them one by one.
    
    for unit in units:
        if unit.name.startswith("ACC-"):
            continue
            
        accommodation = unit.accommodation # Should be ACC-XX already if linked correctly
        floor = unit.floor
        
        if not floor and unit.floor_name:
             floor = frappe.db.get_value("Floor", unit.floor_name, "floor")
        
        if not accommodation:
            print(f"Skipping Unit {unit.name}: Missing accommodation")
            continue

        try:
            counter = get_next_unit_number(accommodation, floor)
            new_name = "{}-F{}-U{}".format(accommodation, floor, counter)
            
            frappe.rename_doc("Accommodation Unit", unit.name, new_name, force=True)
            frappe.db.commit()
        except Exception as e:
             frappe.log_error(f"Failed to rename Accommodation Unit {unit.name}: {str(e)}", "Accommodation Migration Error")

def rename_accommodation_space_records():
    spaces = frappe.get_all("Accommodation Space", fields=["name", "accommodation_unit", "space_type_abbreviation", "accommodation_space_type"], order_by="creation asc")
    
    for space in spaces:
        if space.name.startswith("ACC-"):
            continue
            
        unit = space.accommodation_unit
        abbr = space.space_type_abbreviation
        
        if not abbr and space.accommodation_space_type:
            abbr = frappe.db.get_value("Accommodation Space Type", space.accommodation_space_type, "abbreviation")
            
        if not abbr:
            abbr = "X"
            
        try:
            counter = get_next_space_number(unit, abbr)
            new_name = "{}-{}{}".format(unit, abbr, counter)
            
            frappe.rename_doc("Accommodation Space", space.name, new_name, force=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Failed to rename Accommodation Space {space.name}: {str(e)}", "Accommodation Migration Error")

def rename_bed_records():
    beds = frappe.get_all("Bed", fields=["name", "accommodation_space"], order_by="creation asc")
    
    for bed in beds:
        if bed.name.startswith("ACC-"):
            continue
            
        space = bed.accommodation_space
        
        try:
            counter = get_next_bed_number(space)
            new_name = "{}-{}".format(space, counter)
            
            frappe.rename_doc("Bed", bed.name, new_name, force=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"Failed to rename Bed {bed.name}: {str(e)}", "Accommodation Migration Error")

def update_naming_series():
    """Update ACC- series to 8 so next record is ACC-8"""
    frappe.db.sql("""INSERT INTO `tabSeries` (name, current) VALUES ('ACC-', 8) 
                     ON DUPLICATE KEY UPDATE current = 8""")
    frappe.db.commit()

