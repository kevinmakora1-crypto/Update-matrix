// Copyright (c) 2020, ONE FM and contributors
// For license information, please see license.txt

// ── Status options per process name ──────────────────────────────────────────
var STATUS_MAP = {
  "Job Offer Issuance": ["Pending", "Offer Accepted", "Rejected"],
  "Visa Processing": ["Pending", "Applied", "Issued", "Rejected"],
  "Medical Test": ["Pending", "In Process", "Fit", "Unfit", "Passed", "Failed"],
  "Remedical Test": ["Pending", "Skipped", "In Process", "Fit", "Unfit", "Passed", "Failed"],
  "PCC Clearance": ["Pending", "Applied", "Issued", "Rejected"],
  "Visa Stamping": ["Pending", "Applied", "Issued", "Approved", "Rejected"],
  "Arrival & Deployment": ["Pending", "Arriving", "Completed"]
};

frappe.ui.form.on('Candidate Country Process', {
  agency_country_process: function(frm) {
    set_country_process_details(frm);
  },
  refresh: function(frm) {
    candidate_country_process_flow_btn(frm);
    setup_inline_status_filter(frm);
  }
});

frappe.ui.form.on('Candidate Country Process Details', {
  // ── Expanded row edit form: filter status options ──
  form_render: function(frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    var options = STATUS_MAP[row.process_name] || ["Pending", "In Process", "Completed"];
    var grid_row = frm.fields_dict.agency_process_details.grid.grid_rows_by_docname[cdn];
    if (grid_row && grid_row.grid_form) {
      var status_field = grid_row.grid_form.fields_dict.status;
      if (status_field) {
        status_field.df.options = options.join('\n');
        status_field.refresh();
      }
    }
  },

  // ── Validate status on change ──
  status: function(frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    var allowed = STATUS_MAP[row.process_name];
    if (allowed && !allowed.includes(row.status)) {
      frappe.msgprint({
        title: __('Invalid Status'),
        message: __('"{0}" is not valid for {1}. Allowed: {2}',
          [row.status, row.process_name, allowed.join(', ')]),
        indicator: 'red'
      });
      frappe.model.set_value(cdt, cdn, 'status', 'Pending');
    }
  }
});

// ── Inline grid: intercept click on status cell and filter <select> options ──
var setup_inline_status_filter = function(frm) {
  var grid = frm.fields_dict.agency_process_details;
  if (!grid || !grid.grid || !grid.grid.wrapper) return;

  grid.grid.wrapper.off('click.status_filter').on('click.status_filter',
    '.frappe-control[data-fieldname="status"]', function() {
      var $cell = $(this);
      var $row = $cell.closest('.rows .frappe-control').length
        ? $cell.closest('[data-name]')
        : $cell.closest('.grid-row');
      if (!$row.length) {
        $row = $cell.closest('[data-name]');
      }
      var docname = $row.attr('data-name');
      if (!docname) return;

      var row_data = locals['Candidate Country Process Details'][docname];
      if (!row_data) return;

      var allowed = STATUS_MAP[row_data.process_name]
        || ["Pending", "In Process", "Completed"];

      // Wait for Frappe to render the <select>, then filter it
      setTimeout(function() {
        var $select = $cell.find('select');
        if (!$select.length) return;

        var current_val = $select.val();
        $select.find('option').each(function() {
          var opt_val = $(this).val();
          if (opt_val && !allowed.includes(opt_val)) {
            $(this).remove();
          }
        });
        // Restore current value if still valid
        if (allowed.includes(current_val)) {
          $select.val(current_val);
        }
      }, 50);
    }
  );
};

var set_country_process_details = function(frm) {
  if(frm.doc.agency_country_process){
    frm.doc.agency_process_details = [];
    frappe.model.with_doc("Agency Country Process", frm.doc.agency_country_process, function() {
      var agency_country_process= frappe.model.get_doc("Agency Country Process", frm.doc.agency_country_process)
      $.each(agency_country_process.agency_process_details, function(index, row){
        var d = frm.add_child("agency_process_details");
        d.process_name = row.process_name;
        d.responsible = row.responsible;
        d.duration_in_days = row.duration_in_days;
        d.parallel_group = row.parallel_group || 0;
        d.attachment_required = row.attachment_required;
        d.notes_required = row.notes_required;
        d.reference_type = row.reference_type;
        d.reference_complete_status_field = row.reference_complete_status_field;
        d.reference_complete_status_value = row.reference_complete_status_value;
      });
      
      frm.refresh_field("agency_process_details");
    });
  }
};

var candidate_country_process_flow_btn = function(frm) {
  if(!frm.doc.__islocal && frm.doc.name){
    frappe.call({
      doc: frm.doc,
      method:"get_workflow",
      callback: function(data){
        if(!data.exc){
          var workflow_list = data.message;
          workflow_list.forEach(function(workflow_doctype, i) {
            if(frm.doc.doctype != workflow_doctype.doctype){
              frm.add_custom_button(__(workflow_doctype.doctype), function() {
                if (!("new_doc" in workflow_doctype)){
                  var doclist = frappe.model.sync(workflow_doctype);
                  frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
                }
                else{
                  frappe.route_options = {
                    "candidate_country_process": frm.doc.name
                  };
                  frappe.new_doc(workflow_doctype.doctype);
                }
              },__("Country Process Flow"));
            }
          });
        }
      }
    });
  }
};
