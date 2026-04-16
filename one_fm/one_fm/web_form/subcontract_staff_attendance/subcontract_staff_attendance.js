frappe.ready(function() {
	frappe.web_form.on('ready', () => {
		frappe.web_form.page.add_inner_button(__('Preview Attendance'), () => {
			show_attendance_preview(frappe.web_form);
		});
	});
});

function show_attendance_preview(web_form) {
	const doc = web_form.get_values();
	
	if (!doc.from_date || !doc.to_date) {
		frappe.msgprint(__("Please ensure From Date and To Date are set."));
		return;
	}

	const from_date = moment(doc.from_date);
	const to_date = moment(doc.to_date);
	const days_in_range = to_date.diff(from_date, 'days') + 1;

	const status_map = {
		"Present": "P",
		"Absent": "A",
		"On Leave": "L",
		"Half Day": "HD",
		"Work From Home": "WFH",
		"Day Off": "DO",
		"Client Day Off": "CDO",
		"Fingerprint Appointment": "FA",
		"Medical Appointment": "MA",
		"Holiday": "H",
		"On Hold": "OH"
	};

	let headers = `<th>${__("Employee ID")}</th><th>${__("Employee Name")}</th>`;
	let dates = [];
	for (let i = 0; i < days_in_range; i++) {
		let current_date = moment(from_date).add(i, 'days');
		let is_friday = current_date.day() === 5;
		let display_date = current_date.format("D.M");
		dates.push({date: current_date, is_friday: is_friday, day_num: current_date.date()});
		headers += `<th class="${is_friday ? 'bg-secondary text-white' : ''}" style="min-width: 40px; text-align: center;">${display_date}</th>`;
	}

	let rows = "";
	(doc.subcontractor_staff_attendance_item || []).forEach(row => {
		let cells = `<td>${row.employee_id || ""}</td><td>${row.employee_name || ""}</td>`;
		dates.forEach(d => {
			let val = row[`day_${d.day_num}`] || "";
			if (doc.attendance_record_based_on === "Attendance Status") {
				val = status_map[val] || val;
			} else if (doc.attendance_record_based_on === "Shift Hours") {
				val = row[`day_${d.day_num}_hour`] || "";
			}
			cells += `<td class="${d.is_friday ? 'bg-light' : ''}" style="text-align: center;">${val}</td>`;
		});
		rows += `<tr>${cells}</tr>`;
	});

	const table_html = `
		<div style="overflow-x: auto; max-height: 60vh;">
			<table class="table table-bordered table-sm" style="font-size: 11px; white-space: nowrap;">
				<thead class="bg-light">
					<tr>${headers}</tr>
				</thead>
				<tbody>
					${rows}
				</tbody>
			</table>
		</div>
	`;

	const dialog = new frappe.ui.Dialog({
		title: __("Attendance Preview Matrix"),
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "matrix_html",
				options: table_html
			}
		],
		primary_action_label: __("Close"),
		primary_action: () => dialog.hide()
	});

	if (frappe.is_mobile) {
		dialog.$wrapper.find('.modal-dialog').css('max-width', '100%');
	} else {
		dialog.$wrapper.find('.modal-dialog').css('max-width', '95%');
	}
	dialog.show();
}