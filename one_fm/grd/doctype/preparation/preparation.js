// Copyright (c) 2021, ONE FM and contributors
// For license information, please see license.txt

frappe.ui.form.on('Preparation Record',{
	//set total amunt per employee on the selection of the process
	renewal_or_extend: function(frm, cdt, cdn){
		set_preparation_record_costing(frm, cdt, cdn);
	},
	no_of_years: function(frm, cdt, cdn){
		set_preparation_record_costing(frm, cdt, cdn);
	},
	work_permit_amount: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		caclulate_renewal_extension_cost_total(frm, child);
	},
	medical_insurance_amount: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		caclulate_renewal_extension_cost_total(frm, child);
	},
	residency_stamp_amount: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		caclulate_renewal_extension_cost_total(frm, child);
	},
	civil_id_amount: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		caclulate_renewal_extension_cost_total(frm, child);
	},
	employee: function(frm, cdt, cdn){
		// Debounced batch fetch to avoid multiple quick calls
		if(!frm._employee_dates_timeout){
			frm._employee_dates_timeout = setTimeout(() => {
				fetch_employee_dates_batch(frm);
				frm._employee_dates_timeout = null;
			}, 300);
		}
	}
});

var set_preparation_record_costing = function(frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	if(row.renewal_or_extend){
		if(row.renewal_or_extend == 'Renewal' & !row.no_of_years){
			frappe.model.set_value(row.doctype, row.name, "no_of_years", '1 Year');
			frm.refresh_field('preparation_record');
		}
		frappe.call({
			method: 'one_fm.grd.doctype.preparation.preparation.get_grd_renewal_extension_cost',
			args: {'renewal_or_extend': row.renewal_or_extend, 'no_of_years': row.no_of_years},
			callback: function(r) {
				if(r.message){
					var cost = r.message;
					frappe.model.set_value(row.doctype, row.name, "work_permit_amount", cost.work_permit_amount);
					frappe.model.set_value(row.doctype, row.name, "medical_insurance_amount", cost.medical_insurance_amount);
					frappe.model.set_value(row.doctype, row.name, "residency_stamp_amount", cost.residency_stamp_amount);
					frappe.model.set_value(row.doctype, row.name, "civil_id_amount", cost.civil_id_amount);
					frappe.model.set_value(row.doctype, row.name, "total_amount", cost.total_amount);
					frm.refresh_field('preparation_record');
				}
			}
		});
	}
};

var caclulate_renewal_extension_cost_total = function(frm, child) {
	var total_cost = 0;
	if(child.work_permit_amount && child.work_permit_amount > 0){
		total_cost += child.work_permit_amount;
	}
	if(child.medical_insurance_amount && child.medical_insurance_amount > 0){
		total_cost += child.medical_insurance_amount;
	}
	if(child.residency_stamp_amount && child.residency_stamp_amount > 0){
		total_cost += child.residency_stamp_amount;
	}
	if(child.civil_id_amount && child.civil_id_amount > 0){
		total_cost += child.civil_id_amount;
	}
	frappe.model.set_value(child.doctype, child.name, 'total_amount', total_cost);
	frm.refresh_field('preparation_record');
};

//Set renewal for all employee to facilitate process
frappe.ui.form.on("Preparation", {
	refresh : frm=>{
		if(frm.doc.docstatus==1){
			if(!frappe.user.has_role("HR Manager")){
				cur_frm.fields_dict.preparation_record.grid.update_docfield_property("renewal_or_extend", "allow_on_submit", 0);
				cur_frm.fields_dict.preparation_record.grid.update_docfield_property("no_of_years", "allow_on_submit", 0);
				cur_frm.fields_dict.preparation_record.grid.update_docfield_property("work_permit_amount", "allow_on_submit", 0);
				cur_frm.fields_dict.preparation_record.grid.update_docfield_property("medical_insurance_amount", "allow_on_submit", 0);
				cur_frm.fields_dict.preparation_record.grid.update_docfield_property("residency_stamp_amount", "allow_on_submit", 0);
				cur_frm.fields_dict.preparation_record.grid.update_docfield_property("civil_id_amount", "allow_on_submit", 0);
				
				// Fetch dates on refresh (covers load & reload)
				fetch_employee_dates_batch(frm);
			}
		}

	},
	set_renewal_for_all: function(frm) {
		frappe.call({
			doc: frm.doc,
			method: 'set_renewal_for_all_preparation_record',
			args: {'renew_all': frm.doc.set_renewal_for_all},
			callback: function(r) {
				frm.refresh_field('preparation_record');
			}
		})
	},
});


function fetch_employee_dates_batch(frm){
	if(!frm.doc.preparation_record || frm.doc.preparation_record.length === 0){
		return;
	}
	if(frm.is_new()){
		return; // cannot DB set unsaved rows
	}
	frappe.call({
		method: 'one_fm.grd.doctype.preparation.preparation.update_preparation_employee_dates',
		args: { preparation: frm.doc.name },
		freeze: false,
		callback: function(r){
			// We avoid local field mutation to keep form clean.
			// Optionally, refresh grid rows that were updated so user sees values.
			if(r.message && r.message.updated_rows && r.message.updated_rows.length){
				// Reload only affected child rows values from DB
				// r.message.updated_rows.forEach(rowname => {
				// 	frappe.model.remove_from_locals('Preparation Record', rowname); // force re-fetch
				// });
				frm.refresh_field('preparation_record');
			}
		}
	});
}
