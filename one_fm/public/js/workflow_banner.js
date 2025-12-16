(function() {
    'use strict';
    
    // Store original set_intro method
    const original_set_intro = frappe.ui.form.Form.prototype.set_intro;
    
    // Cache for workflow state banner data to reduce API calls
    const workflow_banner_cache = {};
    
    // Color mapping for workflow states
    const COLOR_MAP = {
        'Success': 'green',
        'Warning': 'orange',
        'Danger': 'red',
        'Primary': 'blue',
        'Info': 'blue',
        'Inverse': 'darkgrey'
    };
    
    // Override set_intro method
    frappe.ui.form.Form.prototype.set_intro = function(txt, color) {
        const frm = this;
        
        // Check if workflow is enabled for this doctype
        if (frm.doc && frm.doc.workflow_state) {
            // Fetch and prepend workflow banner
            fetch_workflow_banner(frm, function(banner_html) {
                if (banner_html) {
                    // Call original set_intro with workflow banner first
                    original_set_intro.call(frm, banner_html.message, banner_html.color);
                }
                
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
    
    // Function to fetch workflow banner message
    function fetch_workflow_banner(frm, callback) {
        const current_state = frm.doc.workflow_state;
        
        if (!current_state) {
            callback(null);
            return;
        }
        
        // Check cache first
        if (workflow_banner_cache[current_state]) {
            callback(workflow_banner_cache[current_state]);
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
                if (r.message) {
                    const banner_data = {
                        message: r.message.message || '',
                        color: COLOR_MAP[r.message.style] || 'blue'
                    };
                    
                    // Cache the result
                    workflow_banner_cache[current_state] = banner_data;
                    callback(banner_data);
                } else {
                    callback(null);
                }
            },
            error: function(r) {
                console.error('Error fetching workflow banner:', r);
                callback(null);
            }
        });
    }
    
    // Clear cache when workflow state changes
    frappe.ui.form.on('*', {
        after_workflow_action: function(frm) {
            // Clear cache for current state
            if (frm.doc.workflow_state && workflow_banner_cache[frm.doc.workflow_state]) {
                delete workflow_banner_cache[frm.doc.workflow_state];
            }
            
            // Refresh to show new banner
            frm.refresh();
        }
    });
    
    console.log('Workflow Banner Wrapper (set_intro) initialized');
})();
