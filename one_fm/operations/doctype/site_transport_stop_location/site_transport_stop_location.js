// Copyright (c) 2026, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site Transport Stop Location', {
    refresh: function (frm) {
        apply_location_filters(frm);
    },
    site_arrangement: function (frm) {
        apply_location_filters(frm);
    }
});

function apply_location_filters(frm) {
    // Filter the Link field for "One Location Many Sites" arrangement
    frm.set_query("transport_stop_location", function () {
        return {
            filters: [
                ["Location", "location_type", "=", "Stop Location"]
            ]
        };
    });

    // Filter the child table location field for "One Site Many Locations" arrangement
    frm.set_query("location", "transport_stop_locations", function () {
        return {
            filters: [
                ["Location", "location_type", "=", "Stop Location"]
            ]
        };
    });

    // Filter the 'site' Link field (in "One Site Many Locations")
    frm.set_query("site", function () {
        return {
            filters: [
                ["Operations Site", "status", "=", "Active"]
            ]
        };
    });

    // Filter 'sites' field in 'sites' child table (in "One Location Many Sites")
    frm.set_query("sites", "sites", function () {
        return {
            filters: [
                ["Operations Site", "status", "=", "Active"]
            ]
        };
    });
}
