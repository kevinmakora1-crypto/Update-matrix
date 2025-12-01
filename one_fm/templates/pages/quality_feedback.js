frappe.ready(() => {
    const container = document.getElementById('quality-feedback-container');
    const docname = container.getAttribute('data-docname');
    
    let selectedLanguage = 'en'; // Default to English
    let selectedLanguageName = 'English';
    let feedbackData = null;
    let languages = [];

    // Fetch languages from backend
    fetchLanguages();

    function fetchLanguages() {
        frappe.call({
            method: 'one_fm.templates.pages.quality_feedback.get_all_languages',
            callback: (r) => {
                if (r.message && r.message.length > 0) {
                    languages = r.message.map(lang => ({
                        code: lang.name,
                        name: lang.language_name || lang.name
                    }));
                    // Show language selector after languages are fetched
                    showLanguageSelector();
                } else {
                    // Fallback if no languages found
                    container.innerHTML = `<div class="alert alert-danger">No languages found. Please contact administrator.</div>`;
                }
            },
            error: () => {
                container.innerHTML = `<div class="alert alert-danger">Error loading languages. Please try again later.</div>`;
            }
        });
    }

    function showLanguageSelector() {
        container.innerHTML = `
            <div class="language-selector-container">
                <div class="language-selector-card">
                    <h2 class="language-selector-title">Select Your Language</h2>
                    <p class="language-selector-subtitle">Please choose your preferred language to continue</p>
                    <div class="language-grid">
                        ${languages.map(lang => `
                            <button class="language-option" data-lang="${lang.code}">
                                ${lang.name}
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;

        // Add click handlers for language selection
        document.querySelectorAll('.language-option').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const langCode = e.target.getAttribute('data-lang');
                selectedLanguage = langCode;
                // Find language name
                const langObj = languages.find(l => l.code === langCode);
                selectedLanguageName = langObj ? langObj.name : langCode;
                container.innerHTML = '<div class="loading-message">Loading form...</div>';
                
                // Fetch feedback data and render form
                fetchFeedbackData();
            });
        });
    }

    function fetchFeedbackData() {
        frappe.call({
            method: 'one_fm.templates.pages.quality_feedback.get_feedback_data',
            args: { docname: docname },
            callback: (r) => {
                if (r.message) {
                    feedbackData = r.message;
                    renderQualityFeedbackForm(feedbackData, docname);
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
    }

    function translateAllContent(data, docname) {
        return new Promise((resolve) => {
            const employeeName = data.employee_name || '[Employee Full Name]';
            const itemType = data.item_type || '[Item_Type]';
            
            // Prepare all texts to translate
            const textsToTranslate = [
                'Hello',
                ', tell us about your Feedback about',
                'Quality Feedback Details',
                'Employee ID:',
                'Operation Site:',
                'Issued On:',
                'Current Feedback Schedule:',
                'Quality Feedback Questions',
                'Survey Question',
                'Rating Option:',
                'Select Rating',
                'Additional Details',
                'Noticed Damage?:',
                'No',
                'Yes',
                'Damage Description:',
                'Describe any damage noticed...',
                'Damage Attachment:',
                'Attach',
                'Feedback:',
                'Share your feedback...',
                'Submit Feedback',
                'Submitting...',
                'Very Poor',
                'Poor',
                'Average',
                'Good',
                'Excellent'
            ];

            // Add question texts
            const questionTexts = (data.questions || []).map(q => q.question || '');
            
            // Batch translate all texts
            frappe.call({
                method: 'one_fm.templates.pages.quality_feedback.translate_multiple',
                args: {
                    texts: textsToTranslate.concat(questionTexts),
                    target_language: selectedLanguage
                },
                callback: (r) => {
                    const translated = r.message || textsToTranslate.concat(questionTexts);
                    const translations = translated.slice(0, textsToTranslate.length);
                    const translatedQuestions = translated.slice(textsToTranslate.length);
                    
                    // Map translated questions back to question objects
                    const questions = (data.questions || []).map((q, idx) => ({
                        ...q,
                        question: translatedQuestions[idx] || q.question
                    }));

                    resolve({
                        translations,
                        questions
                    });
                },
                error: () => {
                    // Return original texts if translation fails
                    resolve({
                        translations: textsToTranslate,
                        questions: data.questions || []
                    });
                }
            });
        });
    }

    async function renderQualityFeedbackForm(data, docname) {
        const employeeName = data.employee_name || '[Employee Full Name]';
        const itemType = data.item_type || '[Item_Type]';
        const employeeId = data.employee_id || '';
        const operationSite = data.operation_site || '';
        const issuedOn = data.issued_on || '';
        const feedbackSchedule = data.current_feedback_schedule || '';

        // Translate all content (or skip translation if English)
        let translations, questions;
        if (selectedLanguage === 'en') {
            // For English, use original texts without translation
            translations = [
                'Hello', ', tell us about your Feedback about', 'Quality Feedback Details',
                'Employee ID:', 'Operation Site:', 'Issued On:', 'Current Feedback Schedule:',
                'Quality Feedback Questions', 'Survey Question', 'Rating Option:', 'Select Rating',
                'Additional Details', 'Noticed Damage?:', 'No', 'Yes', 'Damage Description:',
                'Describe any damage noticed...', 'Damage Attachment:', 'Attach', 'Feedback:',
                'Share your feedback...', 'Submit Feedback', 'Submitting...',
                'Very Poor', 'Poor', 'Average', 'Good', 'Excellent'
            ];
            questions = data.questions || [];
        } else {
            container.innerHTML = '<div class="loading-message">Translating content...</div>';
            const translated = await translateAllContent(data, docname);
            translations = translated.translations;
            questions = translated.questions;
        }

        const [
            helloText, tellAboutText, detailsTitle, employeeIdLabel, operationSiteLabel,
            issuedOnLabel, scheduleLabel, questionsTitle, surveyQuestionText, ratingLabel,
            selectRatingText, additionalDetailsTitle, damageLabel, noText, yesText,
            damageDescLabel, damagePlaceholder, damageAttachmentLabel, attachText,
            feedbackLabel, feedbackPlaceholder, submitText, submittingText,
            veryPoorText, poorText, averageText, goodText, excellentText
        ] = translations;

        container.innerHTML = `
            <div class="quality-feedback-form" data-lang="${selectedLanguage}">
                <div class="form-header-controls">
                    <div class="language-controls">
                        <button class="globe-icon-btn" id="globe-icon" title="Change Language">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="12" cy="12" r="10"></circle>
                                <line x1="2" y1="12" x2="22" y2="12"></line>
                                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                            </svg>
                        </button>
                        <span class="selected-language-display">${selectedLanguageName}</span>
                    </div>
                </div>
                <h2 class="quality-feedback-title">${helloText}, ${employeeName}${tellAboutText} ${itemType}!</h2>
                
                <div class="quality-feedback-section feedback-details-section">
                    <h3 class="section-title">${detailsTitle}</h3>
                    <div class="details-grid">
                        <div class="detail-row">
                            <div class="detail-label">${employeeIdLabel}</div>
                            <div class="detail-value auto-fill">${employeeId}</div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">${operationSiteLabel}</div>
                            <div class="detail-value auto-fill">${operationSite}</div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">${issuedOnLabel}</div>
                            <div class="detail-value auto-fetch">${issuedOn}</div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">${scheduleLabel}</div>
                            <div class="detail-value auto-fetch">${feedbackSchedule}</div>
                        </div>
                    </div>
                </div>

                <div class="quality-feedback-section">
                    <h3 class="section-title">${questionsTitle}</h3>
                    <div class="questions-container" id="questions-container">
                        ${questions.map((question, index) => `
                            <div class="question-row">
                                <div class="question-label">${surveyQuestionText} ${index + 1}:</div>
                                <div class="question-text auto-fetch">${question.question || ''}</div>
                                <div class="rating-label">${ratingLabel}</div>
                                <div class="rating-input-wrapper">
                                    <select class="form-control rating-select" name="question_${index + 1}_rating" data-question-index="${index}">
                                        <option value="">${selectRatingText}</option>
                                        ${generateRatingOptions(question.rating_type, {
                                            veryPoor: veryPoorText,
                                            poor: poorText,
                                            average: averageText,
                                            good: goodText,
                                            excellent: excellentText
                                        })}
                                    </select>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="quality-feedback-section">
                    <h3 class="section-title">${additionalDetailsTitle}</h3>
                    <div class="additional-details-container">
                        <div class="damage-section">
                            <div class="damage-label">${damageLabel}</div>
                            <div class="radio-group">
                                <label class="radio-option">
                                    <input type="radio" name="noticed_damage" value="No" checked>
                                    <span class="radio-label">${noText}</span>
                                </label>
                                <label class="radio-option">
                                    <input type="radio" name="noticed_damage" value="Yes">
                                    <span class="radio-label">${yesText}</span>
                                </label>
                            </div>
                        </div>
                        <div class="damage-description-section damage-field-hidden" id="damage-description-section" style="display: none;">
                            <label class="form-label" for="damage-description">${damageDescLabel} <span class="required-asterisk">*</span></label>
                            <textarea 
                                id="damage-description" 
                                class="form-control damage-textarea" 
                                name="damage_description" 
                                rows="4" 
                                placeholder="${damagePlaceholder}"></textarea>
                        </div>
                        <div class="damage-attachment-section damage-field-hidden" id="damage-attachment-section" style="display: none;">
                            <label class="form-label">${damageAttachmentLabel} <span class="required-asterisk">*</span></label>
                            <div class="attachment-wrapper">
                                <a href="#" class="attach-link" id="attach-link">${attachText}</a>
                                <span class="attachment-file-name" id="attachment-file-name"></span>
                            </div>
                            <input type="file" id="damage-attachment-input" class="d-none" accept="image/*,.pdf">
                        </div>
                        <div class="feedback-section">
                            <label class="form-label" for="feedback-text">${feedbackLabel}</label>
                            <textarea 
                                id="feedback-text" 
                                class="form-control feedback-textarea" 
                                name="feedback_text" 
                                rows="6" 
                                placeholder="${feedbackPlaceholder}"></textarea>
                        </div>
                    </div>
                </div>

                <div class="submit-section">
                    <button type="button" class="btn btn-primary btn-submit-feedback" id="submit-feedback-btn">${submitText}</button>
                </div>

                <div id="feedback-response" class="mt-3"></div>
            </div>
        `;

        // Initialize form interactions
        initializeFormInteractions(docname, submittingText, submitText);
        
        // Handle globe icon click to go back to language selection
        const globeIcon = document.getElementById('globe-icon');
        if (globeIcon) {
            globeIcon.addEventListener('click', () => {
                showLanguageSelector();
            });
        }
    }

    function generateRatingOptions(ratingType, translations = {}) {
        const options = {
            '1-5': ['1', '2', '3', '4', '5'].map(val => `<option value="${val}">${val}</option>`),
            '1-10': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'].map(val => `<option value="${val}">${val}</option>`),
            'satisfaction': [
                `<option value="Very Poor">${translations.veryPoor || 'Very Poor'}</option>`,
                `<option value="Poor">${translations.poor || 'Poor'}</option>`,
                `<option value="Average">${translations.average || 'Average'}</option>`,
                `<option value="Good">${translations.good || 'Good'}</option>`,
                `<option value="Excellent">${translations.excellent || 'Excellent'}</option>`
            ]
        };
        
        return options[ratingType] || options['1-5'].join('');
    }

    function initializeFormInteractions(docname, submittingText, submitText) {
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
                submitFeedbackForm(docname, submittingText, submitText);
            });
        }
    }

    function submitFeedbackForm(docname, submittingText, submitText) {
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
        submitBtn.textContent = submittingText || 'Submitting...';

        frappe.call({
            method: 'one_fm.templates.pages.quality_feedback.submit_feedback',
            args: formData,
            callback: (r) => {
                submitBtn.disabled = false;
                submitBtn.textContent = submitText || 'Submit Feedback';
                
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
                submitBtn.textContent = submitText || 'Submit Feedback';
                responseDiv.innerHTML = `<div class="alert alert-danger">A server error occurred. Please try again later.</div>`;
            }
        });
    }
});
