frappe.ui.form.on('Quality Feedback Template', {
	refresh: function(frm) {
		render_damaged_attachments(frm);
	},
});

const render_damaged_attachments = function (frm) {
	// Don't render attachments for new/unsaved templates
	if (!frm.doc.name || frm.is_new()) {
		return;
	}

	var $wrapper = frm.fields_dict['custom_damaged_attachments_html'].$wrapper;
	
	// Show loading state
	$wrapper.html('<div class="text-center" style="padding: 20px;"><i class="fa fa-spinner fa-spin"></i> ' + __('Loading damaged attachments...') + '</div>');
	
	// Call server method to get damaged attachments
	frappe.call({
		method: 'one_fm.overrides.quality_feedback_template.get_damaged_attachments',
		args: {
			quality_feedback_template: frm.doc.name
		},
		callback: function(r) {
			if (r.message) {
				render_attachments(r.message, $wrapper);
			} else {
				$wrapper.html('<div class="text-center" style="padding: 20px; color: #999;">' + __('No damaged attachments found') + '</div>');
			}
		},
		error: function(r) {
			$wrapper.html('<div class="text-center" style="padding: 20px; color: #d9534f;">' + __('Error loading damaged attachments') + '</div>');
			console.error('Error loading damaged attachments:', r);
		}
	});
};

const render_attachments = function(attachments, $wrapper) {
	if (!attachments || attachments.length === 0) {
		$wrapper.html('<div class="text-center" style="padding: 20px; color: #999;">' + __('No damaged attachments found') + '</div>');
		return;
	}
	
	// Pagination settings
	var page_length = 9; // 3x3 grid = 9 images per page
	var current_page = 1;
	var total_pages = Math.ceil(attachments.length / page_length);
	
	// Function to get full file URL
	var get_file_url = function(file_url) {
		if (!file_url) return '';
		// If already a full URL, return as is
		if (file_url.startsWith('http://') || file_url.startsWith('https://')) {
			return file_url;
		}
		// Otherwise, prepend site URL
		return frappe.urllib.get_full_url(file_url);
	};
	
	// Function to check if file is an image
	var is_image_file = function(file_name) {
		if (!file_name) return false;
		var extension = file_name.split('.').pop().toLowerCase();
		var image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico', 'tiff', 'tif'];
		return image_extensions.indexOf(extension) !== -1;
	};
	
	// Function to render grid with pagination
	var render_grid = function(page) {
		current_page = page;
		var start_index = (page - 1) * page_length;
		var end_index = Math.min(start_index + page_length, attachments.length);
		var page_attachments = attachments.slice(start_index, end_index);
		
		// Generate HTML for 3-column grid
		var grid_html = '<div class="damaged-attachments-grid">';
		for (var i = 0; i < page_attachments.length; i++) {
			if (i % 3 === 0) {
				grid_html += '<div class="row">';
			}
			
			var attachment = page_attachments[i];
			var file_url = get_file_url(attachment.file_url);
			var file_name = attachment.file_name || __('Attachment');
			var is_image = is_image_file(file_name);
			
			if (is_image) {
				// Show image for image files
				grid_html += `
					<div class="col-md-4">
						<div class="image-item" title="${file_name.replace(/"/g, '&quot;')}">
							<img src="${file_url}" alt="${file_name}" class="img-thumbnail" 
								onclick="window.open('${file_url}', '_blank')"
								onerror="this.src='/assets/frappe/images/ui-states/image-loading.svg'">
							<div class="image-title" title="${file_name}">${file_name}</div>
						</div>
					</div>
				`;
			} else {
				// Show file icon for non-image files
				grid_html += `
					<div class="col-md-4">
						<div class="image-item file-item" title="${file_name.replace(/"/g, '&quot;')}">
							<div class="file-icon-wrapper" onclick="window.open('${file_url}', '_blank')">
								<i class="fa fa-file-o fa-4x"></i>
							</div>
							<div class="image-title" title="${file_name}">${file_name}</div>
						</div>
					</div>
				`;
			}
			if (i % 3 === 2 || i === page_attachments.length - 1) {
				grid_html += '</div>';
			}
		}
		grid_html += '</div>';
		
		// Generate pagination controls
		var pagination_html = '';
		if (total_pages > 1) {
			pagination_html = '<div class="damaged-attachments-pagination">';
			pagination_html += '<div class="pagination-info">';
			pagination_html += __('Showing {0} to {1} of {2} images', [start_index + 1, end_index, attachments.length]);
			pagination_html += '</div>';
			pagination_html += '<div class="pagination-controls">';
			
			// Previous button
			if (current_page > 1) {
				pagination_html += `<button class="btn btn-sm btn-secondary pagination-btn" data-page="${current_page - 1}">
					<i class="fa fa-chevron-left"></i> ` + __('Previous') + `
				</button>`;
			} else {
				pagination_html += `<button class="btn btn-sm btn-secondary pagination-btn" disabled>
					<i class="fa fa-chevron-left"></i> ` + __('Previous') + `
				</button>`;
			}
			
			// Page numbers
			pagination_html += '<div class="pagination-numbers">';
			var start_page = Math.max(1, current_page - 2);
			var end_page = Math.min(total_pages, current_page + 2);
			
			if (start_page > 1) {
				pagination_html += `<button class="btn btn-sm btn-secondary pagination-btn" data-page="1">1</button>`;
				if (start_page > 2) {
					pagination_html += '<span class="pagination-ellipsis">...</span>';
				}
			}
			
			for (var p = start_page; p <= end_page; p++) {
				if (p === current_page) {
					pagination_html += `<button class="btn btn-sm btn-primary pagination-btn active" data-page="${p}">${p}</button>`;
				} else {
					pagination_html += `<button class="btn btn-sm btn-secondary pagination-btn" data-page="${p}">${p}</button>`;
				}
			}
			
			if (end_page < total_pages) {
				if (end_page < total_pages - 1) {
					pagination_html += '<span class="pagination-ellipsis">...</span>';
				}
				pagination_html += `<button class="btn btn-sm btn-secondary pagination-btn" data-page="${total_pages}">${total_pages}</button>`;
			}
			
			pagination_html += '</div>';
			
			// Next button
			if (current_page < total_pages) {
				pagination_html += `<button class="btn btn-sm btn-secondary pagination-btn" data-page="${current_page + 1}">
					` + __('Next') + ` <i class="fa fa-chevron-right"></i>
				</button>`;
			} else {
				pagination_html += `<button class="btn btn-sm btn-secondary pagination-btn" disabled>
					` + __('Next') + ` <i class="fa fa-chevron-right"></i>
				</button>`;
			}
			
			pagination_html += '</div>';
			pagination_html += '</div>';
		}
		
		var field_html = `
			<style>
				.damaged-attachments-grid {
					padding: 10px;
					margin-bottom: 20px;
				}
				.damaged-attachments-grid .row {
					display: flex;
					flex-wrap: wrap;
					margin: 0 -5px;
				}
				.damaged-attachments-grid .col-md-4 {
					flex: 0 0 33.333333%;
					max-width: 33.333333%;
					padding: 5px;
					box-sizing: border-box;
				}
				.damaged-attachments-grid .image-item {
					text-align: center;
					border: 1px solid #ddd;
					border-radius: 4px;
					padding: 10px;
					background-color: #fff;
					transition: box-shadow 0.2s;
				}
				.damaged-attachments-grid .image-item:hover {
					box-shadow: 0 2px 8px rgba(0,0,0,0.1);
				}
				.damaged-attachments-grid .image-item img {
					width: 100%;
					height: auto;
					max-height: 200px;
					object-fit: cover;
					margin-bottom: 8px;
					cursor: pointer;
					border-radius: 4px;
				}
				.damaged-attachments-grid .file-item {
					display: flex;
					flex-direction: column;
					align-items: center;
					justify-content: center;
					min-height: 220px;
				}
				.damaged-attachments-grid .file-icon-wrapper {
					width: 100%;
					display: flex;
					align-items: center;
					justify-content: center;
					padding: 40px 20px;
					margin-bottom: 8px;
					cursor: pointer;
					color: #999;
					transition: color 0.2s;
				}
				.damaged-attachments-grid .file-icon-wrapper:hover {
					color: #5e64ff;
				}
				.damaged-attachments-grid .file-icon-wrapper i {
					font-size: 64px;
				}
				.damaged-attachments-grid .image-title {
					font-size: 12px;
					color: #666;
					word-break: break-word;
					font-weight: 500;
				}
				.damaged-attachments-pagination {
					padding: 15px;
					border-top: 1px solid #ddd;
					background-color: #f9f9f9;
				}
				.damaged-attachments-pagination .pagination-info {
					text-align: center;
					margin-bottom: 10px;
					color: #666;
					font-size: 13px;
				}
				.damaged-attachments-pagination .pagination-controls {
					display: flex;
					justify-content: center;
					align-items: center;
					gap: 5px;
					flex-wrap: wrap;
				}
				.damaged-attachments-pagination .pagination-numbers {
					display: flex;
					gap: 5px;
					align-items: center;
					margin: 0 10px;
				}
				.damaged-attachments-pagination .pagination-btn {
					min-width: 40px;
					height: 32px;
					padding: 0 12px;
					border-radius: 4px;
					font-size: 13px;
				}
				.damaged-attachments-pagination .pagination-btn.active {
					background-color: #5e64ff;
					border-color: #5e64ff;
					color: white;
				}
				.damaged-attachments-pagination .pagination-btn:disabled {
					opacity: 0.5;
					cursor: not-allowed;
				}
				.damaged-attachments-pagination .pagination-ellipsis {
					padding: 0 5px;
					color: #666;
				}
			</style>
			${grid_html}
			${pagination_html}
		`;
		
		$wrapper.html(field_html);
		
		// Attach click handlers to pagination buttons
		$wrapper.find('.pagination-btn').on('click', function() {
			var page = parseInt($(this).data('page'));
			if (page && page !== current_page && page >= 1 && page <= total_pages) {
				render_grid(page);
			}
		});
	};
	
	// Initial render
	render_grid(1);
};
