/**
 * INTERVIEW CONSOLE - GOLD STANDARD (M3)
 * 
 * PREVENTION MECHANISM FOR "6-HOUR BLANK SCREEN" ISSUE:
 * 1. CSS is kept entirely in JS (frappe.dom.set_style) to prevent 
 *    the Page loader from misinterpreting CSS @import/rules as JS identifiers.
 * 2. HTML template is kept as pure structural markup.
 * 3. Page initialization uses page.main for direct rendering.
 */
frappe.pages['interview_console'].on_page_load = function (wrapper) {
	try {
		console.log("--- Interview Console Init (Direct Injection Mode) ---");

		// 1. Dynamic Font & CSS Loading
		if (!$('link[href*="Roboto"]').length) {
			$('head').append('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600;700&display=swap">');
		}

		frappe.dom.set_style(`
            body.ic-active .page-head, body.ic-active .page-head-content, body.ic-active .page-title { display: none !important; }
            
            /* FORCE FULL-WIDTH: Override Frappe's .container and .layout-main-section max-width */
            body.ic-active .layout-main-section, 
            body.ic-active .page-content, 
            body.ic-active .container { 
                padding: 0 !important; 
                margin: 0 !important; 
                max-width: none !important; 
                width: 100% !important;
                height: 100% !important; 
            }
            
            /* Restore navbar padding to prevent profile icon from hitting the screen edge */
            body.ic-active .navbar .container,
            body.ic-active .navbar {
                padding-left: 20px !important;
                padding-right: 20px !important;
                width: 100% !important;
            }

            #ic-root {
                display: flex; flex-direction: row; align-items: stretch;
                height: calc(100vh - 105px); 
                width: 100% !important;
                background: #fdfcff; font-family: 'Roboto', 'Segoe UI', Helvetica, Arial, sans-serif;
                overflow: hidden; color: #1e293b; 
                margin: 0 !important; 
                padding: 12px 16px !important; box-sizing: border-box;
            }
            .ic-sidebar {
                width: 260px; min-width: 260px; max-width: 260px;
                flex: 0 0 260px;
                background: #eef0f6; /* Subtle cool-grey/blue Surface Variant */
                display: flex; flex-direction: column; padding: 12px 0 12px 12px;
                border: none;
                border-radius: 16px 0 0 16px;
                margin: 0;
                overflow: hidden; box-sizing: border-box;
                box-shadow: none;
                transition: width 0.4s cubic-bezier(0.2, 0, 0, 1), min-width 0.4s cubic-bezier(0.2, 0, 0, 1), flex 0.4s cubic-bezier(0.2, 0, 0, 1), background 0.4s ease;
            }
            /* When a selection is made, sidebar shrinks slightly and shifts background */
            #ic-root.has-selection .ic-sidebar {
                width: 240px; min-width: 240px; max-width: 240px; flex: 0 0 240px;
                background: #eef5ff; /* Primary Container tint */
            }
            .ic-search-wrap { 
                margin-bottom: 12px; margin-right: 12px; background: #ffffff; border: 1px solid #c4c6d0; 
                border-radius: 50px; padding: 8px 16px; display: flex; 
                align-items: center; flex-shrink: 0; 
                box-shadow: 0 1px 2px rgba(0,0,0,0.02);
            }
            .ic-search-input { border: none; background: transparent; width: 100%; font-size: 13px; font-weight: 400; outline: none; font-family: 'Roboto', sans-serif; }
            .ic-sidebar-header { margin-right: 12px; display: flex; justify-content: space-between; padding: 0 5px 8px 5px; font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; flex-shrink: 0; }
            
            /* Items - M3 Standard Navigation Drawer Item */
            .ic-item { 
                padding: 8px 12px; margin-bottom: 2px; border-radius: 50px; margin-right: 12px;
                cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                background: transparent; border: none; position: relative;
                display: flex; flex-direction: column; gap: 2px;
            }
            .ic-item:hover { background: rgba(0, 0, 0, 0.04); }
            
            /* Active Indicator - Pill Shaped */
            .ic-item.selected { 
                background: #c2e7ff !important; /* M3 Active Indicator Color */
                border: none !important;
                margin-right: 12px; 
                box-shadow: none;
                transform: none;
            }
            .ic-item.selected .ic-item-name { color: #001d35 !important; font-weight: 700; }
            .ic-item.selected .ic-item-id { color: #004a77 !important; }
            
            .ic-item-name { font-size: 11px; font-weight: 600; color: #1e293b; margin-bottom: 0px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; transition: color 0.3s ease; }
            .ic-item-id { font-size: 9px; font-weight: 500; color: #64748b; transition: color 0.3s ease; }
            
            .ic-sb-score { float: right; background: #ffffff; padding: 2px 6px; border-radius: 8px; font-weight: 700; font-size: 9px; color: #475569; position: absolute; right: 12px; top: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
            
            .ic-status-pill { 
                font-size: 9px; font-weight: 600; padding: 2px 6px; 
                border-radius: 6px; display: inline-flex; align-items: center; justify-content: center;
                border: 1px solid transparent; text-transform: none; 
            }
            .status-accepted { background: #dcfce7; color: #14532d; border-color: #bbf7d0; }
            .status-rejected { background: #fee2e2; color: #991b1b; border-color: #fecaca; }
            .status-hold { background: #fef9c3; color: #854d0e; border-color: #fef08a; }
            .status-scored { background: #e0f2fe; color: #075985; border-color: #bae6fd; }
            .status-not-scored { background: #f1f5f9; color: #475569; border-color: #e2e8f0; }
            
            .ic-item.selected .status-scored { background: transparent; border-color: rgba(0, 74, 119, 0.3); color: #004a77; }
            .ic-item.selected .status-not-scored { background: transparent; border-color: rgba(0, 74, 119, 0.3); color: #004a77; }
            
            .ic-main {
                flex: 1 1 0%;
                min-width: 0;
                display: flex; flex-direction: column;
                overflow: hidden; background: #fdfcff;
                border-radius: 0 16px 16px 0;
                transition: padding 0.4s ease;
            }
            #ic-root.has-selection .ic-main {
                padding-left: 8px;
            }
            .ic-header { display: flex; align-items: center; padding: 10px 20px; gap: 15px; border-bottom: 1px solid #f1f5f9; flex-shrink: 0; }
            .ic-header-field { text-align: center; }
            .ic-header-label { 
                font-size: 11px; font-weight: 500; color: #44474e; /* MD3 Label Large */
                text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.1em; 
            }
            .ic-header-value-box { 
                background: white; border: 1px solid #c4c6d0; border-radius: 50px; 
                padding: 6px 18px; font-size: 18px; font-weight: 500; min-width: 60px; 
                color: #1c1b1f; display: flex; align-items: center; justify-content: center;
            }
            .ic-score-pill { 
                background: #d3e3fd; color: #041e49; border-radius: 50px; 
                padding: 8px 30px; font-size: 18px; font-weight: 600; border: none; 
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            .ic-clear-btn { 
                background: white; border: 1px solid #e2e8f0; width: 36px; height: 36px; border-radius: 18px; 
                display: flex; align-items: center; justify-content: center; cursor: pointer; color: #94a3b8; 
                font-size: 16px; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            }
            .ic-clear-btn:hover { 
                color: #ef4444; border-color: #fecaca; background: #fef2f2; 
                transform: scale(1.15) rotate(90deg);
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .ic-clear-btn:active, .ic-clear-btn.expanded { transform: scale(0.9); transition-duration: 0.1s; }
            .ic-actions-right { margin-left: auto; display: flex; gap: 12px; align-items: center; }
            .ic-btn-circular { 
                width: 48px; height: 48px; min-width: 48px; max-width: 48px;
                border-radius: 24px; padding: 0; 
                display: flex; align-items: center; justify-content: center; 
                cursor: pointer; transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
                border: 1px solid transparent; position: relative; overflow: hidden;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1); box-sizing: border-box;
                background: #f1f5f9; color: #475569;
            }
            .ic-btn-circular:hover { 
                transform: scale(1.08) translateY(-1px); 
                box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
            }
            .ic-btn-circular:active, .ic-btn-circular.expanded { 
                min-width: 120px; border-radius: 12px; transform: scale(0.98); 
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.1); 
            }
            .ic-btn-circular .btn-text { 
                max-width: 0; opacity: 0; margin-left: 0; font-size: 13px; 
                transition: all 0.3s ease; text-transform: capitalize; 
                font-weight: 600; white-space: nowrap; 
            }
            .ic-btn-circular:active .btn-text, .ic-btn-circular.expanded .btn-text { 
                max-width: 80px; opacity: 1; margin-left: 10px; 
            }
            .btn-reject { background: #fef2f2; color: #dc2626; border: 1px solid #fee2e2; }
            .btn-hold   { background: #fffcf0; color: #d97706; border: 1px solid #fef3c7; }
            .btn-accept { background: #f0fdf4; color: #16a34a; border: 1px solid #dcfce7; }
            .ic-btn-circular.disabled { background: #f1f5f9 !important; color: #cbd5e1 !important; border: 1px solid #e2e8f0 !important; cursor: not-allowed; pointer-events: none; box-shadow: none; }
            .ic-dashboard-link {
                background: #f0f9ff; color: #0369a1; border: 1px solid #e0f2fe;
                padding: 6px 16px; border-radius: 50px; font-size: 13px;
                font-weight: 600; display: flex; align-items: center; gap: 8px;
                margin-left: 8px; height: 36px; cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            }
            .ic-dashboard-link:hover {
                background: #e0f2fe; transform: scale(1.05);
                box-shadow: 0 4px 8px rgba(3, 105, 161, 0.1);
            }
            .ic-dashboard-link:active, .ic-dashboard-link.expanded {
                transform: scale(0.96); background: #bae6fd;
            }
            .ic-dashboard-link .count-circle {
                background: #0369a1; color: #ffffff; width: 22px; height: 22px;
                border-radius: 50%; display: flex; align-items: center; justify-content: center;
                font-size: 11px; font-weight: 700; box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            .ic-dashboard-link .link-text { margin-left: 0; }
            .ic-matrix-container { 
                flex: 1 1 0%; min-width: 0;
                padding: 16px 20px; margin: 12px 20px 20px 20px; 
                background: #ffffff; border: none; border-radius: 20px;
                overflow: hidden; display: flex; flex-direction: column;
                /* Default State - Locked & Faded (Sharp) */
                transform: translateY(10px);
                opacity: 0.75;
                filter: none;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                transition: transform 0.6s cubic-bezier(0.2, 0, 0, 1), opacity 0.6s cubic-bezier(0.2, 0, 0, 1), filter 0.6s ease, box-shadow 0.6s cubic-bezier(0.2, 0, 0, 1);
            }
            /* Active State - Fully Opaque & Interactive */
            #ic-root.has-selection .ic-matrix-container {
                transform: translateY(0);
                opacity: 1;
                filter: none;
                box-shadow: 0 12px 24px rgba(0,0,0,0.06), 0 4px 8px rgba(0,0,0,0.04);
            }
            table.ic-table { 
                width: 100%; height: 100%; border-collapse: separate; 
                border-spacing: 8px 8px; table-layout: fixed;
            }
            .ic-table th { 
                padding: 6px 4px; font-size: 10px; font-weight: 600; color: #44474e; 
                text-align: center; border: 1px solid #c4c6d0; border-radius: 4px; 
                height: auto; min-height: unset; vertical-align: middle; background: #ffffff; 
                line-height: 1.25; text-transform: none; letter-spacing: normal; 
                white-space: normal; word-break: break-word; overflow: visible;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            }
            /* Style for Category Headers (Top Row) - Pill Shape Wrapper */
            .ic-category-pill {
                display: flex;
                align-items: center; justify-content: center;
                border-radius: 8px;
                padding: 5px 16px;
                font-size: 11px;
                font-weight: 700;
                border: 1px solid rgba(0,0,0,0.1);
                box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                margin: 0;
                width: 100%;
                box-sizing: border-box;
                text-transform: capitalize;
                letter-spacing: 0.02em;
            }
            .ic-table th[colspan] {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                padding: 0 !important;
            }
            /* Style for Question Headers (Bottom Row) - Individual MD3 Cards */
            tr:nth-child(2) th {
                height: 80px; /* Uniform height for all question headers */
                border-radius: 8px !important;
                background: #ffffff !important;
                border: 1px solid rgba(0,0,0,0.08) !important;
                padding: 10px 4px !important;
                box-shadow: none !important;
                vertical-align: middle !important;
                font-size: 8.5px !important; /* Slightly smaller for better fitting */
                line-height: 1.1 !important;
                word-wrap: break-word;
                white-space: normal;
                overflow: hidden;
            }
            .ic-row-num { width: 24px; font-size: 10px; font-weight: 800; color: #94a3b8; text-align: center; font-family: monospace; }
            .ic-cell { 
                padding: 4px; border: 1px solid #e1e2ec; border-radius: 4px; 
                min-height: unset; height: 100%; font-size: 10px; font-weight: 500; color: #1c1b1f; 
                text-align: center; cursor: pointer; transition: all 0.2s ease-out; 
                display: flex; align-items: center; justify-content: center; 
                line-height: 1.25; background: #ffffff; position: relative; overflow: visible;
                word-break: break-word;
            }
            .ic-cell:hover::after {
                content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background-color: #0369a1; opacity: 0.04; pointer-events: none;
            }
            .ic-cell.selected {
                border: 2px solid #22c55e !important;
                color: #14532d !important;
                font-weight: 700;
            }
            .ic-cell.selected::after {
                content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background-color: #22c55e; opacity: 0.12; pointer-events: none;
            }
            .ic-remarks-area { padding: 0; margin-top: 0; background: #ffffff; }
            .ic-remarks-row { padding: 15px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; margin: 0 4px 20px 48px; }
            .ic-remarks-input { width: 100%; height: 120px; border: none; font-size: 13px; font-weight: 400; color: #1e293b; outline: none; resize: none; background: transparent; font-family: 'Roboto', sans-serif; }
        `);

		// 2. Initialize Page Structure
		var page = frappe.ui.make_app_page({
			parent: wrapper,
			title: '',
			single_column: true
		});

		// 3. Render Template into the Main Container
		var content = frappe.render_template('interview_console', {});
		if (!content) throw new Error("Template failed to render");

        // The template should have #ic-root at its top level, ensuring it can receive classes
		$(page.main).empty().append(content);

		// 4. Page Visibility Handlers to prevent CSS leakage
		$(wrapper).on('show', function () {
			$('body').addClass('ic-active');
		});
		$(wrapper).on('hide', function () {
			$('body').removeClass('ic-active');
		});
		// Trigger initial show if already visible
		if ($(wrapper).is(':visible')) $('body').addClass('ic-active');

		setTimeout(function () {
			try {
				init_interview_console(wrapper, page);
			} catch (e) {
				console.error("Logic Init Error:", e);
			}
		}, 150);
	} catch (err) {
		console.error("Global Page Load Error:", err);
		$(wrapper).html('<div style="padding:100px; text-align:center; color:red;"><h3>Page Builder Error</h3><p>' + err.message + '</p></div>');
	}
};

function init_interview_console(wrapper, page) {
	var $w = function (selector) { return $(wrapper).find(selector); };

	// Helper for fuzzy matching question names
	var get_standard_key = function(str) {
		return (str || "").replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
	};

	var MASTER_WORD_MAPPING = {
		"Physical / Body Build (Fitness & Stature)": ["Tall, athletic, well-built.", "Fit, well-proportioned.", "Neutral, average build.", "Fatigued, poor posture.", "Unhealthy, physically brittle."],
		"Quality of Appearance (Grooming & Presence)": ["Crisp, clean, inviting.", "Clean, tidy attire.", "Standard, basic grooming.", "Scruffy or inappropriate.", "Unhygienic or aggressive."],
		"Tell me about a Difficult Situation?": ["Solves complex problems.", "Solves average problems.", "Solves simple problems.", "No solution provided.", "No situation stated."],
		"Tell me about a Difficult Customer you faced?": ["Expert crowd control.", "Manages groups effectively.", "Basic crowd control.", "No crowd control.", "Careless; no control."],
		"Hard Worker (Can you work 12 hours, 16 hours, 24 hours? Can you work 30days without a day off? can you work 2 years without vacation? can you work 1 year without sick leave?)": ["Full 24/7 availability.", "16hr/ takes sick leave.", "Limited shift availability.", "Cannot work 30- days.", "Minimal shift capacity."],
		"Work History (Promotion)": ["International experience.", "Local security promotions.", "Basic security experience.", "Non-security experience.", "No work history."],
		"A customer comes to asking for directions and you do not know the direction what do you do?": ["Guides customer personally.", "Researches then guides.", "Refers to supervisor.", "Defers to others.", "Claims no knowledge."],
		"Technical (Incident Fire + Theft)": ["Full emergency response.", "Follows basic protocols.", "Partial protocol knowledge.", "Major protocol gaps.", "Fails technical check."],
		"English Written": ["Perfect grammar/structure.", "Good; minor errors.", "Readable; limited vocab.", "Poor; many errors.", "Cannot write."],
		"English Read": ["Clear; no skips.", "Reads without hesitation.", "Skips/repeats words.", "Barely reads sentences.", "Cannot read."],
		"English Comprehension": ["Perfect understanding.", "Few clarifications needed.", "Needs many repetitions.", "Poor understanding.", "No understanding."],
		"English Speak": ["Eloquent natural speaker.", "Fluent English speech.", "Reasonable speaking clarity.", "Broken English speech.", "Cannot speak English."]
	};

	var state = {
		selected_applicant: null,
		scores: [], // Dynamic: will be array of selected row (1-5) for each question
		matrix: [],
		applicants: []
	};

	function init() {
		fetch_applicants();
		setup_handlers();
	}

	function render_dynamic_matrix(matrix) {
		if (!matrix || matrix.length === 0) {
			$w('.ic-table').hide();
			$w('#ic-no-matrix-msg').show();
			return;
		}

		$w('.ic-table').show();
		$w('#ic-no-matrix-msg').hide();

		// Group Matrix by Category
		var categories = [];
		var currentCat = null;
		for (var i = 0; i < matrix.length; i++) {
			var catName = matrix[i].category || "General";
			if (!currentCat || currentCat.name !== catName) {
				currentCat = { name: catName, weight: matrix[i].category_weight || "", count: 0, questions: [] };
				categories.push(currentCat);
			}
			currentCat.count++;
			currentCat.questions.push(matrix[i]);
		}

		// Update Headers (Two-Row Header)
		var headerHtml = '<tr><th rowspan="2" style="width: 40px; border: none; background: transparent; box-shadow: none;">Rate</th>';
		
		// Row 1: Categories
		var categoryColors = {
			"PHYSICAL": "#dcfce7", // Original Green
			"Culture / Attitude": "#fff9c4", // Original Yellow/Gold
			"Motivation": "#f3e8ff", // Original Purple
			"Knowledge / Skillset": "#fee2e2", // Original Pink/Red
			"Communication": "#e0f2fe"  // Original Sky Blue
		};
		var categoryTextColors = {
			"PHYSICAL": "#166534",
			"Culture / Attitude": "#854d0e",
			"Motivation": "#6b21a8",
			"Knowledge / Skillset": "#991b1b",
			"Communication": "#0369a1"
		};

		for (var j = 0; j < categories.length; j++) {
			var cat = categories[j];
			var bg = categoryColors[cat.name] || "#f1f5f9";
			var text = categoryTextColors[cat.name] || "#475569";
			
			// Capitalize only first letter of the category name
			var display_name = cat.name.charAt(0).toUpperCase() + cat.name.slice(1).toLowerCase();
			
			headerHtml += '<th colspan="' + cat.count + '">';
			headerHtml += '<div class="ic-category-pill" style="background-color: ' + bg + '; color: ' + text + ';">' + 
						  display_name + '</div></th>';
		}
		headerHtml += '</tr><tr>';

		// Row 2: Questions
		for (var k = 0; k < matrix.length; k++) {
			var q = matrix[k];
			var question_name = q.question;
			var cat_name = q.category || "General";
			var full_color = categoryTextColors[cat_name] || "#475569";
			var bg_tint = "#ffffff";
			
			// Overwrite wording if mapping exists (using fuzzy matching for robustness)
			var standard_q_key = Object.keys(MASTER_WORD_MAPPING).find(key => 
				get_standard_key(key) === get_standard_key(question_name)
			);
			
			if (standard_q_key) {
				q.ratings = MASTER_WORD_MAPPING[standard_q_key];
				question_name = standard_q_key;
			}
			
			headerHtml += '<th style="background-color: ' + bg_tint + ' !important; border-top: 1.5px solid ' + full_color + ' !important; color: #1e293b !important; font-weight: 600; font-size: 8.5px; line-height: 1.1;">' + 
						  question_name + '</th>';
		}
		headerHtml += '</tr>';
		$w('#ic-thead').html(headerHtml);

		// Update Body (5 Rating Rows)
		var bodyHtml = '';
		for (var r = 0; r < 5; r++) {
			var rowNum = 5 - r;
			bodyHtml += '<tr><td class="ic-row-num">' + rowNum + '</td>';
			for (var c = 0; c < matrix.length; c++) {
				var cellText = matrix[c].ratings[r] || "";
				// If cellText is empty and weight is > 0, we could auto-calculate if we wanted, 
				// but let's stick to showing the value from DB for now as per the existing logic.
				bodyHtml += '<td><div class="ic-cell" data-score="' + rowNum + '" data-index="' + c + '">' + cellText + '</div></td>';
			}
			bodyHtml += '</tr>';
		}
		$w('#ic-tbody').html(bodyHtml);
		
		// Initialize scores array if not set
		if (state.scores.length !== matrix.length) {
			state.scores = new Array(matrix.length).fill(0);
		}
	}

	function fetch_applicants() {
		frappe.call({
			method: 'one_fm.one_fm.page.interview_console.interview_console.get_applicant_list',
			callback: function (r) {
				if (r.message) {
					state.applicants = r.message;
					$w('#ic-candidate-count').text(state.applicants.length);
					render_list(state.applicants);
					// Load first applicant's matrix silently to avoid "blank" look
					if (state.applicants.length > 0) {
						load_matrix_silent(state.applicants[0].name);
					}
				} else {
					$w('#ic-list').html('<div style="padding:10px;font-size:11px;color:#94a3b8;">No applicants found.</div>');
				}
			}
		});

		$w('#ic-job-offers-count').text('0');
	}

	function load_matrix_silent(applicant_name) {
		frappe.call({
			method: "one_fm.one_fm.page.interview_console.interview_console.get_applicant_data",
			args: { applicant: applicant_name },
			callback: function (r) {
				if (r.message && r.message.matrix) {
					render_dynamic_matrix(r.message.matrix);
				}
			}
		});
	}

	function render_list(list) {
		var html = '';
		for (var i = 0; i < list.length; i++) {
			var app = list[i];
			var score = app.interview_score || 0;
			var status = app.status || "Open";
			var display_status = status;
			if (["Accepted", "Job Offer Issued", "Shortlisted", "Hired", "Rejected", "Hold"].indexOf(status) === -1) {
				display_status = (score > 0) ? "Scored" : "Not Scored";
			}

			var status_class = "status-not-scored";
			if (display_status === "Scored") status_class = "status-scored";
			if (display_status === "Rejected") status_class = "status-rejected";
			if (display_status === "Hold") status_class = "status-hold";
			if (["Accepted", "Job Offer Issued", "Shortlisted", "Hired"].indexOf(display_status) !== -1) status_class = "status-accepted";

			html += '<div class="ic-item" data-name="' + app.name + '">' +
				'<div class="ic-sb-score">' + score + '</div>' +
				'<div class="ic-item-name">' + app.applicant_name + '</div>' +
				'<div style="display:flex; align-items:center; gap:6px;">' +
				'<span class="ic-item-id">' + app.name + '</span>' +
				'<span class="ic-status-pill ' + status_class + '">' + display_status + '</span>' +
				'</div>' +
				'</div>';
		}
		$w('#ic-list').html(html);

		$w('.ic-item').off('click').on('click', function () {
			var name = $(this).data('name');
			var app = state.applicants.find(function (a) { return a.name === name; });
			select_applicant(app);
		});
	}

	function select_applicant(app) {
		state.selected_applicant = app;
        
        $w('#ic-root').addClass('has-selection');
		$w('.ic-item').removeClass('selected');
		$w('.ic-item[data-name="' + app.name + '"]').addClass("selected");

		frappe.call({
			method: "one_fm.one_fm.page.interview_console.interview_console.get_applicant_data",
			args: { applicant: app.name },
			callback: function (r) {
				var data = r.message || { age: "--", remarks: "", score: 0, status: "Open", job_offers: 0, matrix: [] };
				$w('#ic-age').text(data.age);
				$w('#ic-remarks').val(data.remarks);
				$w('#ic-score-pill').text(data.score + '/100');
				$w('#ic-job-offers-count').text(data.job_offers || 0);

				state.selected_applicant.interview_score = data.score;
				state.selected_applicant.status = data.status;
				state.selected_applicant.job_offer_id = data.job_offer_id || null;
				state.matrix = data.matrix || [];
				
				// Render dynamic matrix
				render_dynamic_matrix(state.matrix);

				// Reset state scores for this matrix
				state.scores = new Array(state.matrix.length).fill(0);
				$w('.ic-cell').removeClass('selected');

				// Update Sidebar UI
				var $item = $w('.ic-item[data-name="' + app.name + '"]');
				$item.find('.ic-sb-score').text(data.score);

				var display_status = data.status;
				if (["Accepted", "Job Offer Issued", "Shortlisted", "Hired", "Rejected", "Hold"].indexOf(data.status) === -1) {
					display_status = (data.score > 0) ? "Scored" : "Not Scored";
				}
				var status_class = "status-not-scored";
				if (display_status === "Scored") status_class = "status-scored";
				if (display_status === "Rejected") status_class = "status-rejected";
				if (display_status === "Hold") status_class = "status-hold";
				if (["Accepted", "Job Offer Issued", "Shortlisted", "Hired"].indexOf(display_status) !== -1) status_class = "status-accepted";

				$item.find('.ic-status-pill').text(display_status)
					.removeClass('status-scored status-rejected status-hold status-accepted status-not-scored')
					.addClass(status_class);

				if (["Accepted", "Job Offer Issued", "Shortlisted", "Hired"].indexOf(data.status) !== -1) {
					$w('#ic-save-btn').addClass('disabled');
				} else {
					$w('#ic-save-btn').removeClass('disabled');
				}
			}
		});
	}

	function setup_handlers() {
		// Cell Click Handler (Delegated since matrix is dynamic)
		$w('#ic-tbody').off('click', '.ic-cell').on('click', '.ic-cell', function () {
			if (!state.selected_applicant) {
				frappe.show_alert({ message: "Select a candidate first", indicator: "orange" });
				return;
			}
			var score = $(this).data('score'); // 1-5
			var index = $(this).data('index'); // column index

			if (state.scores[index] === score) {
				state.scores[index] = 0;
				$(this).removeClass('selected');
			} else {
				$w('.ic-cell[data-index="' + index + '"]').removeClass('selected');
				$(this).addClass('selected');
				state.scores[index] = score;
			}
			update_and_save();
		});

		$w('#ic-reset-btn').on('click', function () {
			state.scores = new Array(state.matrix.length).fill(0);
			$w('.ic-cell').removeClass('selected');
			update_and_save();
		});

		$w('#ic-search').on('input', function () {
			var val = ($(this).val() || "").toLowerCase();
			var filtered = state.applicants.filter(function (a) {
				var name = (a.applicant_name || "").toLowerCase();
				var id = (a.name || "").toLowerCase();
				return name.indexOf(val) !== -1 || id.indexOf(val) !== -1;
			});
			render_list(filtered);
		});

		$w('#ic-remarks').on('input', function () {
			if (state.selected_applicant) update_and_save();
		});

		$w('#ic-job-offers-pill').on('click', function () {
			if (!state.selected_applicant) return;
			var count = parseInt($w('#ic-job-offers-count').text()) || 0;
			if (count === 1 && state.selected_applicant.job_offer_id) {
				frappe.set_route('Form', 'Job Offer', state.selected_applicant.job_offer_id);
			} else if (count > 1) {
				frappe.set_route('List', 'Job Offer', { job_applicant: state.selected_applicant.name });
			} else {
				frappe.show_alert({ message: "This candidate does not have a Job Offer yet.", indicator: "orange" });
			}
		});

		$w('.ic-btn-circular, .ic-clear-btn, .ic-dashboard-link').on('click', function () {
			var $btn = $(this);
			$btn.addClass('expanded');
			setTimeout(function () { $btn.removeClass('expanded'); }, 800);
		});

		$w('#ic-reject-btn').on('click', function () { 
			if (!state.selected_applicant) {
				frappe.show_alert({ message: "Select a candidate first", indicator: "orange" });
				return;
			}
			update_status("Rejected"); 
		});
		$w('#ic-hold-btn').on('click', function () { 
			if (!state.selected_applicant) {
				frappe.show_alert({ message: "Select a candidate first", indicator: "orange" });
				return;
			}
			update_status("Hold"); 
		});
		$w('#ic-save-btn').on('click', function () {
			if (!state.selected_applicant) {
				frappe.show_alert({ message: "Select a candidate first", indicator: "orange" });
				return;
			}

			let d = new frappe.ui.Dialog({
				title: __("Accept Candidate"),
				fields: [
					{
						fieldname: "info",
						fieldtype: "HTML",
						options: `<p>How would you like to proceed with <b>${state.selected_applicant.applicant_name}</b>?</p>`
					}
				],
				primary_action_label: __("Accept & Issue Job Offer"),
				primary_action: function () {
					update_status("Accepted");
					d.hide();
					frappe.show_alert({
						message: __("Applicant Accepted. Magic Link sent to candidate."),
						indicator: "green"
					});
				},
				secondary_action_label: __("Mark as Shortlisted"),
				secondary_action: function () {
					update_status("Shortlisted");
					d.hide();
				}
			});
			d.show();
		});
	}

	function update_and_save() {
		if (!state.selected_applicant) return;
		
		// CALCULATE WEIGHTED SCORE
		// Formula: Sum of ((Selected_Rate / 5) * Weight)
		var weighted_score_sum = 0;
		var total_weight = 0;
		
		for (var i = 0; i < state.matrix.length; i++) {
			var weight = state.matrix[i].weight || 0;
			var selected_rate = state.scores[i] || 0; // 0-5
			
			weighted_score_sum += (selected_rate / 5) * weight;
			total_weight += weight;
		}
		
		var percentage = 0;
		if (total_weight > 0) {
			percentage = Math.round((weighted_score_sum / total_weight) * 100);
		} else {
			// Fallback: If no weights are set, use simple average if scores exist
			var total = 0;
			var active_cols = 0;
			for (var j = 0; j < state.scores.length; j++) {
				if (state.scores[j] > 0) {
					total += state.scores[j];
					active_cols++;
				}
			}
			if (active_cols > 0) percentage = Math.round((total / (active_cols * 5)) * 100);
		}

		var status = state.selected_applicant.status;
		$w('#ic-score-pill').text(percentage + '/100').css({ 'background': '#e0f2fe', 'color': '#0369a1' });
		if (percentage > 0 && status === "Open") status = "Replied";

		save_to_db(percentage, status);

		state.selected_applicant.interview_score = percentage;
		state.selected_applicant.status = status;

		// Refresh UI Pill
		var display_status = status;
		if (["Accepted", "Job Offer Issued", "Shortlisted", "Hired", "Rejected", "Hold"].indexOf(status) === -1) {
			display_status = (percentage > 0) ? "Scored" : "Not Scored";
		}
		var status_class = "status-not-scored";
		if (display_status === "Scored") status_class = "status-scored";
		if (display_status === "Rejected") status_class = "status-rejected";
		if (display_status === "Hold") status_class = "status-hold";
		if (["Accepted", "Job Offer Issued", "Shortlisted", "Hired"].indexOf(display_status) !== -1) status_class = "status-accepted";

		var $item = $w('.ic-item[data-name="' + state.selected_applicant.name + '"]');
		$item.find('.ic-sb-score').text(percentage);
		$item.find('.ic-status-pill').text(display_status)
			.removeClass('status-scored status-rejected status-hold status-accepted status-not-scored')
			.addClass(status_class);
	}

	function save_to_db(score, status) {
		frappe.call({
			method: "one_fm.one_fm.page.interview_console.interview_console.save_interview_data",
			args: {
				applicant: state.selected_applicant.name,
				score: score,
				remarks: $w('#ic-remarks').val(),
				status: status
			},
			callback: function () { }
		});
	}

	function update_status(status) {
		if (!state.selected_applicant) return frappe.msgprint("Select a candidate");
		var score_text = $w('#ic-score-pill').text();
		var score = parseInt(score_text) || 0;

		state.selected_applicant.status = status;
		save_to_db(score, status);

		// Immediate UI update
		var display_status = status;
		if (["Accepted", "Rejected", "Hold"].indexOf(status) === -1) {
			display_status = (score > 0) ? "Scored" : "Not Scored";
		}
		var status_class = "status-not-scored";
		if (display_status === "Scored") status_class = "status-scored";
		if (display_status === "Rejected") status_class = "status-rejected";
		if (display_status === "Hold") status_class = "status-hold";
		if (display_status === "Accepted") status_class = "status-accepted";

		var $item = $w('.ic-item[data-name="' + state.selected_applicant.name + '"]');
		$item.find('.ic-status-pill').text(display_status)
			.removeClass('status-scored status-rejected status-hold status-accepted status-not-scored')
			.addClass(status_class);

		if (["Accepted", "Job Offer Issued", "Shortlisted", "Hired"].indexOf(status) !== -1) {
			$w('#ic-save-btn').addClass('disabled');
		} else {
			$w('#ic-save-btn').removeClass('disabled');
		}

		frappe.show_alert({ message: "Status updated to " + status, indicator: (status === "Rejected" ? "red" : (status === "Hold" ? "orange" : "green")) });
	}

	init();
}
