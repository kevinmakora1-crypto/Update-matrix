frappe.ready(() => {
    const container = document.getElementById('quality-feedback-container');

    const docname = 'QA-FB-1574965'

    // Fetch quality feedback data
    frappe.call({
        method: 'one_fm.templates.pages.quality_feedback.get_feedback_data',
        args: { docname: docname },
        callback: (r) => {
            if (r.message) {
                const data = r.message;
                renderQualityFeedbackForm(data, docname);
            } else {
                container.innerHTML = `<div class="alert alert-danger">Error loading feedback data.</div>`;
            }
        },
        error: () => {
            container.innerHTML = `<div class="alert alert-danger">Error loading feedback data. Please try again later.</div>`;
        },
        freeze: true,
        freeze_message: __('Loading feedback data...')
    });

    function renderQualityFeedbackForm(data, docname) {
        const employeeName = data.employee_name || '[Employee Full Name]';
        const itemType = data.item_type || '[Item_Type]';
        const employeeId = data.employee_id || '';
        const operationSite = data.operation_site || '';
        const issuedOn = data.issued_on || '';
        const feedbackSchedule = data.current_feedback_schedule || '';
        const questions = data.questions || [];

        container.innerHTML = `
            <div class="quality-feedback-form">
                <h2 class="quality-feedback-title">Hello, ${employeeName}, tell us about your Feedback about ${itemType}!</h2>
                
                <div class="quality-feedback-section">
                    <h3 class="section-title">Quality Feedback Details</h3>
                    <div class="details-grid">
                        <div class="detail-row">
                            <div class="detail-label">Employee ID:</div>
                            <div class="detail-value auto-fill">${employeeId}</div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">Operation Site:</div>
                            <div class="detail-value auto-fill">${operationSite}</div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">Issued On:</div>
                            <div class="detail-value auto-fetch">${issuedOn}</div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">Current Feedback Schedule:</div>
                            <div class="detail-value auto-fetch">${feedbackSchedule}</div>
                        </div>
                    </div>
                </div>

                <div class="quality-feedback-section">
                    <h3 class="section-title">Quality Feedback Questions</h3>
                    <div class="questions-container" id="questions-container">
                        ${questions.map((question, index) => `
                            <div class="question-row">
                                <div class="question-label">Survey Question ${index + 1}:</div>
                                <div class="question-text auto-fetch">${question.question || ''}</div>
                                <div class="rating-label">Rating Option:</div>
                                <div class="rating-input-wrapper">
                                    <select class="form-control rating-select" name="question_${index + 1}_rating" data-question-index="${index}">
                                        <option value="">Select Rating</option>
                                        ${generateRatingOptions(question.rating_type)}
                                    </select>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="quality-feedback-section">
                    <h3 class="section-title">Additional Details</h3>
                    <div class="additional-details-container">
                        <div class="damage-section">
                            <div class="damage-label">Noticed Damage?:</div>
                            <div class="radio-group">
                                <label class="radio-option">
                                    <input type="radio" name="noticed_damage" value="No" checked>
                                    <span class="radio-label">No</span>
                                </label>
                                <label class="radio-option">
                                    <input type="radio" name="noticed_damage" value="Yes">
                                    <span class="radio-label">Yes</span>
                                </label>
                            </div>
                        </div>
                        <div class="damage-description-section damage-field-hidden" id="damage-description-section" style="display: none;">
                            <label class="form-label" for="damage-description">Damage Description: <span class="required-asterisk">*</span></label>
                            <textarea 
                                id="damage-description" 
                                class="form-control damage-textarea" 
                                name="damage_description" 
                                rows="4" 
                                placeholder="Describe any damage noticed..."></textarea>
                        </div>
                        <div class="damage-attachment-section damage-field-hidden" id="damage-attachment-section" style="display: none;">
                            <label class="form-label">Damage Attachment: <span class="required-asterisk">*</span></label>
                            <div class="attachment-wrapper">
                                <a href="#" class="attach-link" id="attach-link">Attach</a>
                                <span class="attachment-file-name" id="attachment-file-name"></span>
                            </div>
                            <input type="file" id="damage-attachment-input" class="d-none" accept="image/*,.pdf">
                        </div>
                        <div class="feedback-section">
                            <label class="form-label" for="feedback-text">Feedback:</label>
                            <textarea 
                                id="feedback-text" 
                                class="form-control feedback-textarea" 
                                name="feedback_text" 
                                rows="6" 
                                placeholder="Share your feedback..."></textarea>
                        </div>
                    </div>
                </div>

                <div class="submit-section">
                    <button type="button" class="btn btn-primary btn-submit-feedback" id="submit-feedback-btn">Submit Feedback</button>
                </div>

                <div id="feedback-response" class="mt-3"></div>
            </div>
        `;

        // Initialize form interactions
        initializeFormInteractions(docname);
    }

    function generateRatingOptions(ratingType) {
        const options = {
            '1-5': ['1', '2', '3', '4', '5'].map(val => `<option value="${val}">${val}</option>`),
            '1-10': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'].map(val => `<option value="${val}">${val}</option>`),
            'satisfaction': [
                '<option value="Very Poor">Very Poor</option>',
                '<option value="Poor">Poor</option>',
                '<option value="Average">Average</option>',
                '<option value="Good">Good</option>',
                '<option value="Excellent">Excellent</option>'
            ]
        };
        
        return options[ratingType] || options['1-5'].join('');
    }

    function initializeFormInteractions(docname) {
        // Handle damage visibility toggle
        const damageRadioButtons = document.querySelectorAll('input[name="noticed_damage"]');
        const damageDescriptionSection = document.getElementById('damage-description-section');
        const damageAttachmentSection = document.getElementById('damage-attachment-section');
        const damageDescriptionField = document.getElementById('damage-description');
        const damageAttachmentInput = document.getElementById('damage-attachment-input');

        damageRadioButtons.forEach(radio => {
            radio.addEventListener('change', (e) => {
                const isYes = e.target.value === 'Yes';
                
                if (isYes) {
                    // Show damage fields with fade animation
                    damageDescriptionSection.style.display = 'flex';
                    damageAttachmentSection.style.display = 'flex';
                    setTimeout(() => {
                        damageDescriptionSection.classList.remove('damage-field-hidden');
                        damageAttachmentSection.classList.remove('damage-field-hidden');
                    }, 10);
                    
                    // Make fields required
                    if (damageDescriptionField) {
                        damageDescriptionField.setAttribute('required', 'required');
                    }
                    if (damageAttachmentInput) {
                        damageAttachmentInput.setAttribute('required', 'required');
                    }
                } else {
                    // Hide damage fields with fade animation
                    damageDescriptionSection.classList.add('damage-field-hidden');
                    damageAttachmentSection.classList.add('damage-field-hidden');
                    
                    setTimeout(() => {
                        damageDescriptionSection.style.display = 'none';
                        damageAttachmentSection.style.display = 'none';
                        // Clear values
                        if (damageDescriptionField) {
                            damageDescriptionField.value = '';
                            damageDescriptionField.removeAttribute('required');
                        }
                        if (damageAttachmentInput) {
                            damageAttachmentInput.value = '';
                            damageAttachmentInput.removeAttribute('required');
                            document.getElementById('attachment-file-name').textContent = '';
                        }
                    }, 300);
                }
            });
        });

        // Handle file attachment
        const attachLink = document.getElementById('attach-link');
        const attachmentInput = document.getElementById('damage-attachment-input');
        const fileNameDisplay = document.getElementById('attachment-file-name');

        if (attachLink && attachmentInput) {
            attachLink.addEventListener('click', (e) => {
                e.preventDefault();
                attachmentInput.click();
            });

            attachmentInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    fileNameDisplay.textContent = e.target.files[0].name;
                    fileNameDisplay.classList.add('file-attached');
                }
            });
        }

        // Handle form submission
        const submitBtn = document.getElementById('submit-feedback-btn');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => {
                submitFeedbackForm(docname);
            });
        }
    }

    function submitFeedbackForm(docname) {
        const formData = {
            docname: docname,
            ratings: [],
            noticed_damage: document.querySelector('input[name="noticed_damage"]:checked')?.value || 'No',
            damage_description: document.getElementById('damage-description')?.value || '',
            feedback_text: document.getElementById('feedback-text')?.value || ''
        };

        // Collect ratings
        document.querySelectorAll('.rating-select').forEach((select, index) => {
            formData.ratings.push({
                question_index: index,
                rating: select.value
            });
        });

        // Validate required fields
        const missingRatings = formData.ratings.filter(r => !r.rating);
        if (missingRatings.length > 0) {
            frappe.msgprint(__('Please provide ratings for all questions.'));
            return;
        }

        if (!formData.feedback_text.trim()) {
            frappe.msgprint(__('Please provide your feedback.'));
            return;
        }

        // Validate damage fields if damage is noticed
        if (formData.noticed_damage === 'Yes') {
            if (!formData.damage_description.trim()) {
                frappe.msgprint(__('Please provide a damage description.'));
                document.getElementById('damage-description').focus();
                return;
            }
            
            const attachmentFile = document.getElementById('damage-attachment-input')?.files?.[0];
            if (!attachmentFile) {
                frappe.msgprint(__('Please attach a damage photo or document.'));
                return;
            }
        }

        const submitBtn = document.getElementById('submit-feedback-btn');
        const responseDiv = document.getElementById('feedback-response');
        
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';

        frappe.call({
            method: 'one_fm.templates.pages.quality_feedback.submit_feedback',
            args: formData,
            callback: (r) => {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit Feedback';
                
                if (r.message && r.message.success) {
                    responseDiv.innerHTML = `<div class="alert alert-success">Thank you! Your feedback has been submitted successfully.</div>`;
                    // Optionally redirect or reset form
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } else {
                    responseDiv.innerHTML = `<div class="alert alert-danger">${r.message?.message || 'An error occurred while submitting your feedback. Please try again.'}</div>`;
                }
            },
            error: () => {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit Feedback';
                responseDiv.innerHTML = `<div class="alert alert-danger">A server error occurred. Please try again later.</div>`;
            }
        });
    }
});
