frappe.listview_settings['Designation'] = {
    onload: function(listview) {
        listview.filter_area.add([["Designation", "disabled", "=", 0]]);
    }
};



