frappe.ui.form.on('Contact', {
    after_save: function (frm) {

        if (!frm.is_new()){
            // Construct the new name based on the form data
            let new_name = (frm.doc.first_name + " " + frm.doc.last_name).trim();

            // Check if the new name is different from the current doc name
        
            if (new_name !== frm.doc.name) {
                let new_url = frappe.urllib.get_base_url() + '/app/contact/' + encodeURIComponent(new_name);
                window.location.href = new_url;
            }
        }
    }
});
