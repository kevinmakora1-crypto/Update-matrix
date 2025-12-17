(function() {
    'use strict';
    
    // Store original methods
    const original_set_intro = frappe.ui.form.Form.prototype.set_intro;
    const original_refresh = frappe.ui.form.Form.prototype.refresh;
    
    // Cache for workflow state banner data to reduce API calls
    const workflow_banner_cache = {};

    // Flag to prevent infinite recursion
    let is_showing_workflow_banner = false;
    
    // Color mapping for workflow states
    const COLOR_MAP = {
        'Success': 'green',
        'Warning': 'orange',
        'Danger': 'red',
        'Primary': 'blue',
        'Info': 'blue',
        'Inverse': 'darkgrey'
    };
    
    // Override refresh method to automatically show workflow banner
    frappe.ui.form.Form.prototype.refresh = function(docname) {
        const frm = this;
        // Call original refresh first
        original_refresh.call(frm, docname);

        // Show workflow banner after refresh
        if (frm.doc && frm.doc.workflow_state && !is_showing_workflow_banner) {
            show_workflow_banner_on_load(frm);
        }
    };

    // Override set_intro method to prepend workflow banner
    frappe.ui.form.Form.prototype.set_intro = function(txt, color) {
        const frm = this;

        // Prevent recursion
        if (is_showing_workflow_banner) {
            return original_set_intro.call(frm, txt, color);
        }
        
        // Check if workflow is enabled for this doctype
        if (frm.doc && frm.doc.workflow_state) {
            is_showing_workflow_banner = true;

            // Fetch and prepend workflow banner
            fetch_workflow_banner(frm, function(banner_data) {
                if (banner_data && banner_data.message) {
                    // Call original set_intro with workflow banner first
                    original_set_intro.call(frm, banner_data.message, banner_data.color);
                }
                is_showing_workflow_banner = false;
                // Then append the original intro message if provided
                if (txt) {
                    original_set_intro.call(frm, txt, color);
                }
            });
        } else {
            // No workflow, call original method normally
            original_set_intro.call(frm, txt, color);
        }
    };

    // Function to show workflow banner on form load
    function show_workflow_banner_on_load(frm) {
        is_showing_workflow_banner = true;

        fetch_workflow_banner(frm, function(banner_data) {
            if (banner_data && banner_data.message) {
                original_set_intro.call(frm, banner_data.message, banner_data.color);
            }
            is_showing_workflow_banner = false;
        });
    }
    
    // Function to fetch workflow banner message
    function fetch_workflow_banner(frm, callback) {
        const current_state = frm.doc.workflow_state;
        const cache_key = `${frm.doctype}:${current_state}`;

        if (!current_state) {
            callback(null);
            return;
        }
        
        // Check cache first
        if (workflow_banner_cache[cache_key]) {
            callback(workflow_banner_cache[cache_key]);
            return;
        }
        
        // Fetch from server
        frappe.call({
            method: 'one_fm.api.utils.get_workflow_state_banner_message',
            args: {
                doctype: frm.doc.doctype,
                workflow_state: frm.doc.workflow_state
            },
            callback: function(r) {
                if (r.message && r.message.message) {
                    const banner_data = {
                        message: r.message.message,
                        color: COLOR_MAP[r.message.style] || 'blue'
                    };
                    // Cache the result
                    workflow_banner_cache[cache_key] = banner_data;
                    callback(banner_data);
                } else {
                    // Cache null to avoid repeated lookups
                    workflow_banner_cache[cache_key] = null;
                    callback(null);
                }
            },
            error: function(r) {
                callback(null);
            }
        });
    }
    
    // Clear cache when workflow state changes
    frappe.ui.form.on('*', {
        after_workflow_action: function(frm) {
            // Clear cache for current doctype
            const cache_key = `${frm.doctype}:${frm.doc.workflow_state}`;
            if (workflow_banner_cache[cache_key]) {
                delete workflow_banner_cache[cache_key];
            }
        }
    });
})();