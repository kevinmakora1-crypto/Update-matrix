frappe.ready(() => {
    const container = document.getElementById('quality-feedback-container');
    const docname = container.getAttribute('data-docname');
    
    let selectedLanguage = 'en'; // Default to English
    let selectedLanguageName = 'English';
    let feedbackData = null;
    let languages = [];
    let formSubmitted = false; // Track if form was submitted

    // Show dummy loading at the start
    showLoader('Initializing...', [
        'Loading Quality Feedback...',
        'Preparing interface...',
        'Almost ready...'
    ]);

    // Add a small delay for dummy loading, then fetch languages
    setTimeout(() => {
        fetchLanguages();
    }, 1500);

    // Show engaging loader with progress (full screen)
    function showLoader(message, progressMessages = []) {
        const messages = progressMessages.length > 0 ? progressMessages : [message];
        let currentMessageIndex = 0;
        
        container.innerHTML = `
            <div class="loader-container">
                <div class="loader-wrapper">
                    <div class="progress-spinner">
                        <div class="spinner-ring"></div>
                        <div class="spinner-ring"></div>
                        <div class="spinner-ring"></div>
                        <div class="spinner-ring"></div>
                    </div>
                    <div class="loader-content">
                        <div class="loader-text" id="loader-text">${messages[0]}</div>
                        <div class="loader-progress">
                            <div class="progress-bar" id="progress-bar"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Animate progress bar
        const progressBar = document.getElementById('progress-bar');
        const loaderText = document.getElementById('loader-text');
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 2;
            if (progress > 90) progress = 90; // Don't reach 100% until done
            if (progressBar) {
                progressBar.style.width = progress + '%';
            }
            
            // Change message periodically
            if (messages.length > 1 && progress % 30 === 0) {
                currentMessageIndex = (currentMessageIndex + 1) % messages.length;
                if (loaderText) {
                    loaderText.style.opacity = '0';
                    setTimeout(() => {
                        loaderText.textContent = messages[currentMessageIndex];
                        loaderText.style.opacity = '1';
                    }, 200);
                }
            }
        }, 100);

        // Return function to stop loader
        return (immediate = false) => {
            clearInterval(progressInterval);
            if (progressBar) {
                progressBar.style.width = '100%';
            }
            
            const loaderContainer = document.querySelector('.loader-container');
            if (loaderContainer) {
                if (immediate) {
                    // Remove immediately without fade animation
                    loaderContainer.remove();
                } else {
                    // Fade out animation
                    loaderContainer.style.opacity = '0';
                    setTimeout(() => loaderContainer.remove(), 300);
                }
            }
        };
    }

    // Show submit loader as overlay (doesn't replace container)
    function showSubmitLoader(message, progressMessages = []) {
        const messages = progressMessages.length > 0 ? progressMessages : [message];
        let currentMessageIndex = 0;
        
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'loader-overlay';
        overlay.innerHTML = `
            <div class="loader-wrapper overlay-loader">
                <div class="progress-spinner">
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                    <div class="spinner-ring"></div>
                </div>
                <div class="loader-content">
                    <div class="loader-text" id="submit-loader-text">${messages[0]}</div>
                    <div class="loader-progress">
                        <div class="progress-bar" id="submit-progress-bar"></div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        // Animate progress bar
        const progressBar = document.getElementById('submit-progress-bar');
        const loaderText = document.getElementById('submit-loader-text');
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 2;
            if (progress > 90) progress = 90;
            if (progressBar) {
                progressBar.style.width = progress + '%';
            }
            
            // Change message periodically
            if (messages.length > 1 && progress % 30 === 0) {
                currentMessageIndex = (currentMessageIndex + 1) % messages.length;
                if (loaderText) {
                    loaderText.style.opacity = '0';
                    setTimeout(() => {
                        loaderText.textContent = messages[currentMessageIndex];
                        loaderText.style.opacity = '1';
                    }, 200);
                }
            }
        }, 100);

        // Return function to stop loader
        return () => {
            clearInterval(progressInterval);
            if (progressBar) {
                progressBar.style.width = '100%';
                setTimeout(() => {
                    overlay.style.opacity = '0';
                    setTimeout(() => overlay.remove(), 300);
                }, 300);
            }
        };
    }

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
        // Don't show language selector if form was already submitted
        if (formSubmitted) {
            return;
        }

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
                
                // Show loader with progress messages
                const stopLoader = showLoader('Preparing form...', [
                    'Preparing form...',
                    'Loading your details...',
                    'Fetching feedback questions...',
                    'Almost ready...'
                ]);
                
                // Fetch feedback data and render form
                fetchFeedbackData(stopLoader);
            });
        });
    }

    function fetchFeedbackData(stopLoaderCallback) {
        frappe.call({
            method: 'one_fm.templates.pages.quality_feedback.get_feedback_data',
            args: { docname: docname },
            callback: (r) => {
                if (r.message) {
                    feedbackData = r.message;
                    // Don't stop loader yet - keep it running until form is rendered
                    renderQualityFeedbackForm(feedbackData, docname, stopLoaderCallback);
                } else {
                    if (stopLoaderCallback) stopLoaderCallback();
                    container.innerHTML = `<div class="alert alert-danger">Error loading feedback data.</div>`;
                }
            },
            error: () => {
                if (stopLoaderCallback) stopLoaderCallback();
                container.innerHTML = `<div class="alert alert-danger">Error loading feedback data. Please try again later.</div>`;
            }
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

    async function renderQualityFeedbackForm(data, docname, stopLoaderCallback) {
        // Update loader message to show we're preparing the form
        const loaderText = document.getElementById('loader-text');
        if (loaderText) {
            loaderText.textContent = 'Preparing your form...';
        }
        
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
            // Update loader message for translation
            if (loaderText) {
                loaderText.textContent = 'Translating content...';
            }
            
            const translated = await translateAllContent(data, docname);
            translations = translated.translations;
            questions = translated.questions;
            
            // Update loader message to show form is being rendered
            if (loaderText) {
                loaderText.textContent = 'Rendering form...';
            }
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

        // Form HTML is now set - loader is automatically replaced by innerHTML assignment
        // Clear loader callback interval if it exists (loader HTML is already gone)
        if (stopLoaderCallback) {
            // Just clear the interval, don't try to remove loader (it's already replaced)
            try {
                stopLoaderCallback(true);
            } catch(e) {
                // Ignore if callback fails (loader already gone)
            }
        }

        // Initialize form interactions immediately
        initializeFormInteractions(docname, submittingText, submitText);
        
        // Handle globe icon click to go back to language selection
        const globeIcon = document.getElementById('globe-icon');
        if (globeIcon) {
            globeIcon.addEventListener('click', () => {
                // Don't allow going back to language selector if form was submitted
                if (!formSubmitted) {
                    showLanguageSelector();
                }
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
        let attachmentFile = null;
        if (formData.noticed_damage === 'Yes') {
            if (!formData.damage_description.trim()) {
                frappe.msgprint(__('Please provide a damage description.'));
                document.getElementById('damage-description').focus();
                return;
            }
            
            attachmentFile = document.getElementById('damage-attachment-input')?.files?.[0];
            if (!attachmentFile) {
                frappe.msgprint(__('Please attach a damage photo or document.'));
                return;
            }
        }

        const submitBtn = document.getElementById('submit-feedback-btn');
        const responseDiv = document.getElementById('feedback-response');
        
        submitBtn.disabled = true;
        const originalButtonText = submitBtn.textContent;
        
        // Show submission loader as overlay
        const stopSubmitLoader = showSubmitLoader('Submitting your feedback...', [
            'Validating your feedback...',
            'Saving ratings...',
            'Processing submission...',
            'Almost done...'
        ]);

        // Upload file first if damage attachment exists, then submit feedback
        if (attachmentFile) {
            uploadDamageAttachment(attachmentFile, docname, formData, stopSubmitLoader, submitBtn, originalButtonText, responseDiv);
        } else {
            // No attachment, submit directly
            submitFeedbackData(formData, stopSubmitLoader, submitBtn, originalButtonText, responseDiv);
        }
    }

    function uploadDamageAttachment(file, docname, formData, stopSubmitLoader, submitBtn, originalButtonText, responseDiv) {
        // Upload file using XMLHttpRequest (more reliable)
        const xhr = new XMLHttpRequest();
        const uploadFormData = new FormData();

        xhr.open('POST', '/api/method/upload_file', true);
        xhr.setRequestHeader('X-Frappe-CSRF-Token', frappe.csrf_token);
        xhr.setRequestHeader('Accept', 'application/json');

        uploadFormData.append('file', file);
        uploadFormData.append('is_private', '1');
        uploadFormData.append('folder', 'Home/Attachments');
        uploadFormData.append('doctype', 'Quality Feedback');
        uploadFormData.append('docname', docname);
        uploadFormData.append('fieldname', 'custom_damage_attachment');

        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response && response.message) {
                            const fileUrl = response.message.file_url || response.message.message?.file_url;
                            const fileName = response.message.file_name || file.name;
                            
                            if (fileUrl) {
                                // File uploaded successfully, now include file URL in formData
                                formData.damage_attachment_url = fileUrl;
                                formData.damage_attachment_name = fileName;
                                
                                // Submit feedback with attachment
                                submitFeedbackData(formData, stopSubmitLoader, submitBtn, originalButtonText, responseDiv);
                            } else {
                                throw new Error('File URL not received');
                            }
                        } else {
                            throw new Error('Invalid response format');
                        }
                    } catch (error) {
                        if (stopSubmitLoader) stopSubmitLoader();
                        submitBtn.disabled = false;
                        submitBtn.textContent = originalButtonText;
                        responseDiv.innerHTML = `<div class="alert alert-danger">Error uploading file: ${error.message}. Please try again.</div>`;
                    }
                } else {
                    if (stopSubmitLoader) stopSubmitLoader();
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalButtonText;
                    responseDiv.innerHTML = `<div class="alert alert-danger">Error uploading file (Status: ${xhr.status}). Please try again.</div>`;
                }
            }
        };

        xhr.onerror = function() {
            if (stopSubmitLoader) stopSubmitLoader();
            submitBtn.disabled = false;
            submitBtn.textContent = originalButtonText;
            responseDiv.innerHTML = `<div class="alert alert-danger">Network error while uploading file. Please try again.</div>`;
        };

        xhr.send(uploadFormData);
    }

    function submitFeedbackData(formData, stopSubmitLoader, submitBtn, originalButtonText, responseDiv) {
        frappe.call({
            method: 'one_fm.templates.pages.quality_feedback.submit_feedback',
            args: formData,
            callback: (r) => {
                if (stopSubmitLoader) stopSubmitLoader();
                
                submitBtn.disabled = false;
                submitBtn.textContent = originalButtonText;
                
                if (r.message && r.message.success) {
                    formSubmitted = true; // Mark as submitted to prevent going back to language selector
                    
                    // Show success message
                    responseDiv.innerHTML = `
                        <div class="alert alert-success success-message-box">
                            <div class="success-icon">✓</div>
                            <div class="success-content">
                                <h4>Success!</h4>
                                <p>Thank you! Your feedback has been submitted successfully.</p>
                            </div>
                        </div>
                    `;
                    
                    // Disable form fields
                    document.querySelectorAll('input, select, textarea, button').forEach(el => {
                        if (el.id !== 'globe-icon') {
                            el.disabled = true;
                        }
                    });
                    
                    // Scroll to success message
                    responseDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else {
                    // Show error message without losing form values
                    responseDiv.innerHTML = `<div class="alert alert-danger error-message-box">${r.message?.message || 'An error occurred while submitting your feedback. Please try again.'}</div>`;
                    
                    // Scroll to error message
                    responseDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            },
            error: () => {
                if (stopSubmitLoader) stopSubmitLoader();
                
                submitBtn.disabled = false;
                submitBtn.textContent = originalButtonText;
                
                // Show error message without losing form values
                responseDiv.innerHTML = `<div class="alert alert-danger error-message-box">A server error occurred. Please try again later.</div>`;
                
                // Scroll to error message
                responseDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    }
});
