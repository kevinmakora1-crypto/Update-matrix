// Copyright (c) 2023, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Subcontract Staff Shortlist', {
	refresh: function(frm) {
	},
	set_full_name:function(frm,cdt,cdn,lang){
		let row = locals[cdt][cdn]
		if(lang =='en'){
			let name_array = [row.first_name,row.second_name,row.third_name,row.fourth_name,row.last_name]
			row.full_name = name_array.join(' ')
		}
		else{
			let name_array = [row.first_name_in_arabic,row.second_name_in_arabic,row.third_name_in_arabic,row.fourth_name_in_arabic,row.last_name_in_arabic]
			row.full_name_in_arabic = name_array.join(' ')
		}
		frm.refresh_fields()
	},
	default_designation: function(frm) {
		$.each(frm.doc.subcontract_staff_shortlist_detail || [], function(i, item) {
			frappe.model.set_value('Subcontract Staff Shortlist Detail', item.name, 'designation', frm.doc.default_designation);
		});
	}
});


frappe.ui.form.on('Subcontract Staff Shortlist Detail', {
	first_name:function(frm,cdt,cdn){
		frm.events.set_full_name(frm,cdt,cdn,'en')
	},
	second_name:function(frm,cdt,cdn){
		frm.events.set_full_name(frm,cdt,cdn,'en')
	},
	third_name:function(frm,cdt,cdn){
		frm.events.set_full_name(frm,cdt,cdn,'en')
	},
	fourth_name:function(frm,cdt,cdn){
		frm.events.set_full_name(frm,cdt,cdn,'en')
	},
	last_name:function(frm,cdt,cdn){
		frm.events.set_full_name(frm,cdt,cdn,'en')
	},
	first_name_in_arabic:function(frm,cdt,cdn){
		frm.events.set_full_name(frm,cdt,cdn,'ar')
	},
	second_name_in_arabic:function(frm,cdt,cdn){
		frm.events.set_full_name(frm,cdt,cdn,'ar')
	},
	third_name_in_arabic:function(frm,cdt,cdn){
		frm.events.set_full_name(frm,cdt,cdn,'ar')
	},
	fourth_name_in_arabic:function(frm,cdt,cdn){
		frm.events.set_full_name(frm,cdt,cdn,'ar')
	},
	last_name_in_arabic:function(frm,cdt,cdn){
		frm.events.set_full_name(frm,cdt,cdn,'ar')
	},
	subcontract_staff_shortlist_detail_add: function (frm, cdt, cdn) {
		var row = frappe.get_doc(cdt, cdn);
		if (!row.designation) {
			frm.script_manager.copy_from_first_row("subcontract_staff_shortlist_detail", row, "designation");
		}
		if(!row.designation) row.designation = frm.doc.default_designation;
	},
	
	// OCR Event Handlers
	id_type: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Clear Civil ID fields when switching to Visa Copy
		if (row.id_type === "Visa Copy") {
			frappe.model.set_value(cdt, cdn, 'civil_id_no', '');
			frappe.model.set_value(cdt, cdn, 'civil_id_expiry_date', '');
		}
		
		frm.refresh_field('subcontract_staff_shortlist_detail');
	},
	
	upload_document_btn: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Create file uploader
		new frappe.ui.FileUploader({
			folder: 'Home',
			on_success: (file_doc) => {
				// Set the file URL using standard Frappe API
				frappe.model.set_value(cdt, cdn, 'attach_document', file_doc.file_url);
				
				// Handle Civil ID OCR
				if (row.id_type === "Civil ID") {
					frappe.show_alert({
						message: __('Extracting data from Civil ID, please wait...'),
						indicator: 'blue'
					}, 5);
					
					frappe.call({
						method: 'one_fm.subcontract.doctype.subcontract_staff_shortlist_detail.subcontract_staff_shortlist_detail.trigger_ocr',
						args: {
							file_url: file_doc.file_url,
							id_type: row.id_type,
							subcontractor: frm.doc.subcontractor
						},
						callback: function(r) {
							if (r.message && r.message.success) {
								// Apply OCR results using standard Frappe API
								if (r.message.data.civil_id_no) {
									frappe.model.set_value(cdt, cdn, 'civil_id_no', r.message.data.civil_id_no);
								}
								if (r.message.data.civil_id_expiry_date) {
									frappe.model.set_value(cdt, cdn, 'civil_id_expiry_date', r.message.data.civil_id_expiry_date);
								}
								if (r.message.data.date_of_birth) {
									frappe.model.set_value(cdt, cdn, 'date_of_birth', r.message.data.date_of_birth);
								}
								
								frappe.show_alert({ 
									message: __('Civil ID data extracted successfully'), 
									indicator: 'green' 
								}, 3);
								
								if (r.message.warnings && r.message.warnings.length > 0) {
									r.message.warnings.forEach(w => frappe.msgprint({ 
										title: __('Warning'), 
										indicator: 'orange', 
										message: w 
									}));
								}
							} else {
								frappe.msgprint({ 
									title: __('OCR Failed'), 
									indicator: 'red', 
									message: r.message.message || __('Failed to extract data') 
								});
							}
						},
						error: function() {
							frappe.msgprint({ 
								title: __('Error'), 
								indicator: 'red', 
								message: __('An error occurred while processing') 
							});
						}
					});
				}
			}
		});
	}
});
