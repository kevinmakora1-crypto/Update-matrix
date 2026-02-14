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
	
	attach_document: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Only trigger OCR for Civil ID type
		if (row.id_type !== "Civil ID") {
			return;
		}
		
		// Check if file is attached
		if (!row.attach_document) {
			return;
		}
		
		// Get the row index to find it after save
		let row_index = row.idx - 1;
		
		// Show loading message
		frappe.show_alert({
			message: __('Extracting data from Civil ID, please wait...'),
			indicator: 'blue'
		}, 5);
		
		// Save the parent document first to ensure child row has a proper name
		frm.save().then(() => {
			// After save, get the updated row using the index
			let updated_row = frm.doc.subcontract_staff_shortlist_detail[row_index];
			
			if (!updated_row) {
				frappe.msgprint({
					title: __('Error'),
					indicator: 'red',
					message: __('Could not find the row after save')
				});
				return;
			}
			
			// Trigger OCR processing with the correct row name
			frappe.call({
				method: 'one_fm.subcontract.doctype.subcontract_staff_shortlist_detail.subcontract_staff_shortlist_detail.trigger_ocr',
				args: {
					docname: updated_row.name,
					file_url: updated_row.attach_document
				},
				callback: function(r) {
					if (r.message && r.message.success) {
						// Populate fields with extracted data
						if (r.message.data.civil_id_no) {
							frappe.model.set_value(cdt, updated_row.name, 'civil_id_no', r.message.data.civil_id_no);
						}
						if (r.message.data.civil_id_expiry_date) {
							frappe.model.set_value(cdt, updated_row.name, 'civil_id_expiry_date', r.message.data.civil_id_expiry_date);
						}
						if (r.message.data.date_of_birth) {
							frappe.model.set_value(cdt, updated_row.name, 'date_of_birth', r.message.data.date_of_birth);
						}
						
						// Show success message
						frappe.show_alert({
							message: __('Civil ID data extracted successfully'),
							indicator: 'green'
						}, 3);
						
						// Show warnings if any
						if (r.message.warnings && r.message.warnings.length > 0) {
							r.message.warnings.forEach(function(warning) {
								frappe.msgprint({
									title: __('Warning'),
									indicator: 'orange',
									message: warning
								});
							});
						}
						
						frm.refresh_field('subcontract_staff_shortlist_detail');
					} else {
						console.log("OCR Failed: ", r.message)
						// Show error message
						frappe.msgprint({
							title: __('OCR Failed'),
							indicator: 'red',
							message: r.message.message || __('Failed to extract data from the document')
						});
					}
				},
				error: function(r) {
					frappe.msgprint({
						title: __('Error'),
						indicator: 'red',
						message: __('An error occurred while processing the document')
					});
				}
			});
		}).catch(() => {
			frappe.msgprint({
				title: __('Error'),
				indicator: 'red',
				message: __('Please save the document first before uploading Civil ID')
			});
		});
	}
});
