frappe.web_form.after_load = function() {
	// Auto-populate Subcontractor Name on load using jQuery for visual display
	frappe.call({
		method: "one_fm.api.doc_methods.user.get_my_supplier",
		callback: function(r) {
			if (r.message) {
				$('[data-fieldname="subcontractor_name"] .control-value').html(r.message);
				frappe.web_form.supplier_name = r.message; // store it for the fetch button
			}
		}
	});

	// Inject Fetch Button
	let fetch_btn = $('<button class="btn btn-primary btn-sm mt-3 mb-4" id="fetch_attendance_btn">Fetch Attendance Record</button>');
	$('.frappe-control[data-fieldname="attendance_record_based_on"]').after(fetch_btn);

	fetch_btn.on('click', function(e) {
		e.preventDefault();
		let from_date = frappe.web_form.get_value("from_date");
		let to_date = frappe.web_form.get_value("to_date");
		let based_on = frappe.web_form.get_value("attendance_record_based_on");
		
		if (!from_date || !to_date || !based_on) {
			frappe.msgprint("Please fill From Date, To Date and Attendance Record Based On.");
			return;
		}
		
		let supplier = frappe.web_form.supplier_name;
		if (!supplier) {
			frappe.msgprint("Subcontractor Name not loaded yet.");
			return;
		}

		frappe.call({
			method: "one_fm.one_fm.doctype.subcontract_staff_attendance.subcontract_staff_attendance.api_fetch_subcontractor_staff",
			args: {
				subcontractor_name: supplier,
				from_date: from_date,
				to_date: to_date,
				attendance_record_based_on: based_on
			},
			callback: function(res) {
				if(res.message) {
					// Web Form set_value sometimes fails on Grids. Set explicitly and refresh:
					let grid = frappe.web_form.get_field("subcontractor_staff_attendance_item").grid;
					grid.df.data = res.message;
					grid.refresh();

					frappe.msgprint({title: "Success", message: "Attendance records fetched. You can now review and save.", indicator: "green"});
				}
			}
		});
	});

	// State Management for Existing Documents
	if (frappe.web_form.doc && frappe.web_form.doc.name) {
		let state = frappe.web_form.doc.workflow_state || "Draft";
		
		// Instantly route users to Edit mode from the List Page if the document is a Draft
		if (state === "Draft" && !window.location.pathname.endsWith('/edit')) {
			window.location.replace(window.location.pathname + "/edit");
			return;
		}
		
		// Hide the native Frappe Edit button using hard CSS injection to fully lock out non-draft editing (beats async rendering)
		if (!window.location.pathname.endsWith('/edit')) {
			$('<style>.edit-button { display: none !important; }</style>').appendTo('head');
		}

		// Inject Status Badge
		let color = state === "Draft" ? "orange" : (state === "Pending Operations Supervisor" ? "blue" : "green");
		let badge = `<div class="mt-2 mb-4"><span class="indicator-pill ${color}">${state}</span></div>`;
		$('.web-form-header').append(badge);

		if (state === "Draft") {
			// Add Submit Button ONLY to the bottom action bar. Use type="button" so it doesn't trigger standard HTML form POST.
			let submit_btn = $('<button type="button" class="btn btn-success btn-sm ml-2">Submit</button>');
			$('.web-form-actions').last().append(submit_btn);
			
			submit_btn.on('click', function(e) {
				e.preventDefault();
				frappe.confirm("Are you sure you want to completely submit this attendance record? Once submitted, you cannot edit it.", function() {
					frappe.call({
						method: "one_fm.api.doc_methods.user.submit_attendance",
						args: {
							docname: frappe.web_form.doc.name
						},
						callback: function(r) {
							if (!r.exc) {
								frappe.msgprint({title: "Submitted", indicator: "green", message: "Document successfully submitted."});
								setTimeout(() => { window.location.href = "/subcontractor-attendance"; }, 2000);
							}
						}
					});
				});
			});
		} else {
			// Not Draft -> Lock the form (if they bypassed reading)
			$('form input, form select, form textarea, form button').not('.btn-download').prop('disabled', true);
			$('.web-form-actions .btn-primary').hide(); // Hide Save button
			$('#fetch_attendance_btn').hide();          // Hide Fetch button
			$('.grid-add-row, .grid-remove-rows, .grid-row-check').hide(); // Hide grid editing
		}
	}
};

frappe.web_form.after_save = function() {
	frappe.msgprint({
		title: __("Saved"),
		indicator: "green",
		message: __("Attendance Record has been saved successfully as Draft.")
	});
	setTimeout(function() {
		if (frappe.web_form.doc && frappe.web_form.doc.name) {
			window.location.href = "/subcontractor-attendance";
		}
	}, 1500);
};