frappe.pages['dmarc_dashboard'].on_page_load = function(wrapper) {
	console.log("DMARC Dashboard: on_page_load started");
	
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'DMARC Monitoring Dashboard',
		single_column: true
	});

	page.set_primary_action('Refresh', () => {
		fetch_and_render(page, wrapper);
	}, 'refresh');

	fetch_and_render(page, wrapper);
}

function fetch_and_render(page, wrapper) {
	console.log("DMARC Dashboard: fetch_and_render called");
	
	// Try multiple common Frappe page content selectors
	const $body = $(wrapper).find('.layout-main-section, .page-content, .frappe-page-content').first();
	
	if (!$body.length) {
		console.error("DMARC Dashboard: Could not find main content section in page wrapper");
		return;
	}

	$body.html('<div class="text-muted p-5 text-center dmarc-loading">Fetching DMARC statistics...</div>');

	frappe.call({
		method: 'one_fm.developer.page.dmarc_dashboard.dmarc_dashboard.get_dashboard_data',
		callback: function(r) {
			console.log("DMARC Dashboard: API response received", r);
			
			// Remove loading indicator
			$body.find('.dmarc-loading').remove();
			$body.empty();

			if (r.message && !r.message.error) {
				render_content($body, r.message);
			} else {
				const err_msg = r.message ? r.message.error : 'No response from server';
				$body.html('<div class="alert alert-danger">Error: ' + err_msg + '</div>');
				console.error("DMARC Dashboard Error:", err_msg);
			}
		}
	});
}

function format_num(v) {
	return (v || 0).toLocaleString();
}

function render_content($container, data) {
	console.log("DMARC Dashboard: Rendering content started");
	
	const pass_rate_color = data.pass_rate >= 95 ? 'text-success' : 'text-danger';
	
	// Create the layout
	$container.append(`
		<div class="row mb-4">
			<div class="col-sm-3">
				<div class="frappe-card p-3 text-center">
					<div class="text-muted small">Total Reports</div>
					<div class="h3 font-weight-bold text-primary">${format_num(data.total_reports)}</div>
				</div>
			</div>
			<div class="col-sm-3">
				<div class="frappe-card p-3 text-center">
					<div class="text-muted small">Messages Scanned</div>
					<div class="h3 font-weight-bold text-primary">${format_num(data.total_messages)}</div>
				</div>
			</div>
			<div class="col-sm-3">
				<div class="frappe-card p-3 text-center">
					<div class="text-muted small">Overall Pass Rate</div>
					<div class="h3 font-weight-bold ${pass_rate_color}">${(data.pass_rate || 0).toFixed(1)}%</div>
				</div>
			</div>
			<div class="col-sm-3">
				<div class="frappe-card p-3 text-center">
					<div class="text-muted small">Spoofing Attempts</div>
					<div class="h3 font-weight-bold text-danger">${format_num(data.spoofing_attempts)}</div>
				</div>
			</div>
		</div>
		
		<div class="row mb-4">
			<div class="col-md-8">
				<div class="frappe-card p-3">
					<div class="font-weight-bold mb-3">Daily Email Volume</div>
					<div class="chart-daily-area" style="min-height: 250px;"></div>
				</div>
			</div>
			<div class="col-md-4">
				<div class="frappe-card p-3">
					<div class="font-weight-bold mb-3">Overall Breakdown</div>
					<div class="chart-breakdown-area" style="min-height: 250px;"></div>
				</div>
			</div>
		</div>
		
		<div class="row mb-4">
			<div class="col-md-6">
				<div class="frappe-card p-3">
					<div class="font-weight-bold mb-3">Top 10 Source IPs</div>
					<div class="chart-ips-area" style="min-height: 250px;"></div>
				</div>
			</div>
			<div class="col-md-6">
				<div class="frappe-card p-3">
					<div class="font-weight-bold mb-3">Reports by Organization</div>
					<div class="chart-orgs-area" style="min-height: 250px;"></div>
				</div>
			</div>
		</div>

		<div class="frappe-card p-3">
			<div class="font-weight-bold mb-3 text-danger">Recent Spoofing Alerts</div>
			<div class="table-responsive">
				<table class="table table-sm table-hover table-borderless">
					<thead>
						<tr class="text-muted small uppercase">
							<th>Date</th>
							<th>Source IP</th>
							<th>Country</th>
							<th>Reverse DNS</th>
							<th class="text-right">Msgs</th>
							<th>Action</th>
						</tr>
					</thead>
					<tbody class="alert-rows"></tbody>
				</table>
			</div>
		</div>
	`);

	// Use setTimeout to ensure the browser has parsed the new HTML
	setTimeout(() => {
		try {
			console.log("DMARC Dashboard: Initializing charts");
			
			const daily_el = $container.find('.chart-daily-area').get(0);
			const breakdown_el = $container.find('.chart-breakdown-area').get(0);
			const ips_el = $container.find('.chart-ips-area').get(0);
			const orgs_el = $container.find('.chart-orgs-area').get(0);

			if (daily_el && data.daily_volume && data.daily_volume.labels && data.daily_volume.labels.length) {
				new frappe.Chart(daily_el, {
					data: data.daily_volume,
					type: 'line',
					height: 250,
					colors: ['#28a745', '#dc3545']
				});
			}

			if (breakdown_el) {
				new frappe.Chart(breakdown_el, {
					data: data.breakdown,
					type: 'donut',
					height: 250,
					colors: ['#28a745', '#dc3545']
				});
			}

			if (ips_el) {
				new frappe.Chart(ips_el, {
					data: data.top_ips,
					type: 'bar',
					height: 250,
					colors: ['#007bff']
				});
			}

			if (orgs_el) {
				new frappe.Chart(orgs_el, {
					data: data.org_reports,
					type: 'bar',
					height: 250,
					colors: ['#17a2b8']
				});
			}
			console.log("DMARC Dashboard: Charts initialized successfully");
		} catch (err) {
			console.error("DMARC Dashboard: Chart Render Error", err);
		}
	}, 300);

	// Alerts Table
	const $rows = $container.find('.alert-rows');
	if (data.alerts && data.alerts.length) {
		data.alerts.forEach(a => {
			const badge = a.disposition === 'reject' ? 'badge-danger' : 
						  a.disposition === 'quarantine' ? 'badge-warning' : 'badge-light';
			
			$rows.append(`
				<tr class="${a.disposition === 'reject' ? 'table-danger' : ''}">
					<td class="small">${frappe.datetime.str_to_user(a.date)}</td>
					<td class="font-weight-bold">${a.source_ip}</td>
					<td>${a.source_country || '-'}</td>
					<td class="small text-muted">${a.source_reverse_dns || '-'}</td>
					<td class="text-right">${format_num(a.message_count)}</td>
					<td><span class="badge ${badge}">${a.disposition}</span></td>
				</tr>
			`);
		});
	} else {
		$rows.append('<tr><td colspan="6" class="text-center text-muted p-4">No alerts found.</td></tr>');
	}
}
