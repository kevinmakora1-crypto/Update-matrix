# Copyright (c) 2026, ONE FM and contributors
# For license information, please see license.txt
"""
Patch: Migrate Contract Item operational fields to Contract Items Operation.

Uses direct SQL inserts/updates to avoid triggering Frappe document validation,
which would fail due to mandatory fields that may not yet be populated.
"""

import frappe
from frappe.utils import now


def execute():
    # Fields to migrate from Contract Item to Contract Items Operation
    contract_items = frappe.db.sql("""
        SELECT
            ci.parent,
            ci.item_code,
            ci.item_type,
            ci.count,
            ci.rate_type,
            ci.service_type,
            ci.is_daily_operation_handled_by_us,
            ci.off_type,
            ci.days_off_category,
            ci.no_of_days_off,
            ci.select_specific_days,
            ci.sunday,
            ci.monday,
            ci.tuesday,
            ci.wednesday,
            ci.thursday,
            ci.friday,
            ci.saturday,
            ci.site
        FROM `tabContract Item` ci
        WHERE ci.item_code IS NOT NULL
    """, as_dict=1)

    if not contract_items:
        frappe.logger().info("Patch migrate_contract_item_to_operations: No Contract Items found to migrate.")
        return

    migrated = 0
    updated = 0
    skipped = 0
    now_ts = now()
    user = "Administrator"

    for ci in contract_items:
        if not ci.parent or not ci.item_code:
            skipped += 1
            continue

        # Check if a matching row already exists in Contract Items Operation
        existing_name = frappe.db.get_value(
            "Contract Items Operation",
            {"parent": ci.parent, "item_code": ci.item_code},
            "name"
        )

        if existing_name:
            # Update existing row — only set fields that are not already filled
            frappe.db.sql("""
                UPDATE `tabContract Items Operation`
                SET
                    item_type = COALESCE(NULLIF(item_type, ''), %(item_type)s),
                    count = COALESCE(NULLIF(count, 0), %(count)s),
                    rate_type = COALESCE(NULLIF(rate_type, ''), %(rate_type)s),
                    service_type = COALESCE(NULLIF(service_type, ''), %(service_type)s),
                    is_daily_operation_handled_by_us = COALESCE(NULLIF(is_daily_operation_handled_by_us, ''), %(is_daily_operation_handled_by_us)s),
                    off_type = COALESCE(NULLIF(off_type, ''), %(off_type)s),
                    days_off_category = COALESCE(NULLIF(days_off_category, ''), %(days_off_category)s),
                    no_of_days_off = COALESCE(NULLIF(no_of_days_off, 0), %(no_of_days_off)s),
                    select_specific_days = %(select_specific_days)s,
                    sunday = %(sunday)s,
                    monday = %(monday)s,
                    tuesday = %(tuesday)s,
                    wednesday = %(wednesday)s,
                    thursday = %(thursday)s,
                    friday = %(friday)s,
                    saturday = %(saturday)s,
                    site = COALESCE(NULLIF(site, ''), %(site)s),
                    modified = %(now_ts)s,
                    modified_by = %(user)s
                WHERE name = %(existing_name)s
            """, {
                "item_type": ci.item_type or "",
                "count": ci.count or 0,
                "rate_type": ci.rate_type or "",
                "service_type": ci.service_type or "",
                "is_daily_operation_handled_by_us": ci.is_daily_operation_handled_by_us or "",
                "off_type": ci.off_type or "",
                "days_off_category": ci.days_off_category or "",
                "no_of_days_off": ci.no_of_days_off or 0,
                "select_specific_days": ci.select_specific_days or 0,
                "sunday": ci.sunday or 0,
                "monday": ci.monday or 0,
                "tuesday": ci.tuesday or 0,
                "wednesday": ci.wednesday or 0,
                "thursday": ci.thursday or 0,
                "friday": ci.friday or 0,
                "saturday": ci.saturday or 0,
                "site": ci.site or "",
                "now_ts": now_ts,
                "user": user,
                "existing_name": existing_name,
            })
            updated += 1
        else:
            # Get max idx for this parent to set correct row index
            max_idx = frappe.db.sql("""
                SELECT COALESCE(MAX(idx), 0) FROM `tabContract Items Operation`
                WHERE parent = %s
            """, ci.parent)[0][0]

            new_name = frappe.generate_hash(length=10)

            frappe.db.sql("""
                INSERT INTO `tabContract Items Operation`
                    (name, parent, parenttype, parentfield, idx,
                     item_code, item_type, count, rate_type,
                     service_type, is_daily_operation_handled_by_us,
                     off_type, days_off_category, no_of_days_off,
                     select_specific_days,
                     sunday, monday, tuesday, wednesday, thursday, friday, saturday,
                     site,
                     creation, modified, owner, modified_by, docstatus)
                VALUES
                    (%(name)s, %(parent)s, 'Contracts', 'contract_items_operation', %(idx)s,
                     %(item_code)s, %(item_type)s, %(count)s, %(rate_type)s,
                     %(service_type)s, %(is_daily_operation_handled_by_us)s,
                     %(off_type)s, %(days_off_category)s, %(no_of_days_off)s,
                     %(select_specific_days)s,
                     %(sunday)s, %(monday)s, %(tuesday)s, %(wednesday)s, %(thursday)s, %(friday)s, %(saturday)s,
                     %(site)s,
                     %(now_ts)s, %(now_ts)s, %(user)s, %(user)s, 0)
            """, {
                "name": new_name,
                "parent": ci.parent,
                "idx": max_idx + 1,
                "item_code": ci.item_code,
                "item_type": ci.item_type or "",
                "count": ci.count or 0,
                "rate_type": ci.rate_type or "",
                "service_type": ci.service_type or "",
                "is_daily_operation_handled_by_us": ci.is_daily_operation_handled_by_us or "",
                "off_type": ci.off_type or "",
                "days_off_category": ci.days_off_category or "",
                "no_of_days_off": ci.no_of_days_off or 0,
                "select_specific_days": ci.select_specific_days or 0,
                "sunday": ci.sunday or 0,
                "monday": ci.monday or 0,
                "tuesday": ci.tuesday or 0,
                "wednesday": ci.wednesday or 0,
                "thursday": ci.thursday or 0,
                "friday": ci.friday or 0,
                "saturday": ci.saturday or 0,
                "site": ci.site or "",
                "now_ts": now_ts,
                "user": user,
            })
            migrated += 1

    frappe.db.commit()
    frappe.logger().info(
        f"Patch migrate_contract_item_to_operations: "
        f"Migrated {migrated} new rows, updated {updated} existing rows, skipped {skipped} rows."
    )
