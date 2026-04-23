frappe.ui.form.on("Penalty And Investigation", {
	onload: function(frm) {
		if (frm.is_new()) {
			frm.set_value("issuance_date", frappe.datetime.get_today());
			frm.set_value("incident_date", frappe.datetime.get_today());
		}
	},
	applied_penalty_code: function(frm) {
		frm.trigger("fetch_penalty_details");
	},
	applied_level: function(frm) {
		frm.trigger("fetch_penalty_details");
	},
	employee: function(frm) {
		frm.trigger("fetch_employee_details");
	},
	incident_date: function(frm) {
		frm.trigger("fetch_employee_details");
	},
	fetch_employee_details: function(frm) {
		if (!frm.doc.employee) return;

		let set_details = (site, project) => {
			if (site) frm.set_value("location", site);
			if (project) frm.set_value("project", project);
		};

		if (frm.doc.incident_date) {
			frappe.db.get_list("Employee Schedule", {
				filters: {
					employee: frm.doc.employee,
					date: frm.doc.incident_date,
					employee_availability: "Working"
				},
				fields: ["site", "project"],
				limit: 1
			}).then(res => {
				if (res && res.length > 0) {
					set_details(res[0].site, res[0].project);
				} else {
					// Fallback to Employee Master
					frappe.db.get_value("Employee", frm.doc.employee, ["site", "project"], (r) => {
						if (r) set_details(r.site, r.project);
					});
				}
			});
		} else {
			// No incident date, fallback to master
			frappe.db.get_value("Employee", frm.doc.employee, ["site", "project"], (r) => {
				if (r) set_details(r.site, r.project);
			});
		}
	},
	fetch_penalty_details: function(frm) {
		if (!frm.doc.applied_penalty_code || !frm.doc.applied_level) {
			frm.set_value("deduction_type", "");
			frm.set_value("salary_deduction_days", 0);
			return;
		}

		frappe.model.with_doc("Penalty Code", frm.doc.applied_penalty_code, function() {
			let pc = frappe.get_doc("Penalty Code", frm.doc.applied_penalty_code);
			if (pc && pc.penalty_level) {
				const level_map = {
					"1": "1st",
					"2": "2nd",
					"3": "3rd",
					"4": "4th",
					"5": "5th"
				};
				const target_level = level_map[frm.doc.applied_level];
				const row = pc.penalty_level.find(d => d.offence_level === target_level);
				if (row) {
					frm.set_value("deduction_type", row.deduction_type);
					frm.set_value("salary_deduction_days", row.salary_deduction_days);
				} else {
					frm.set_value("deduction_type", "");
					frm.set_value("salary_deduction_days", 0);
				}
			}
		});
	}
});
