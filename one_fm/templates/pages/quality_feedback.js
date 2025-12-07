frappe.ready(() => {
    const container = document.getElementById('quality-feedback-container');
    const docname = container.getAttribute('data-docname');
    
    let selectedLanguage = 'en'; // Default to English
    let selectedLanguageName = 'English';
    let languages = [];
    let formSubmitted = false; // Track if form was submitted
    let currentLoaderTimeouts = []; // Store all setTimeout IDs for cleanup

    // Show loading at the start
    showLoader('Initializing...', [
        'Loading Quality Feedback...',
        'Preparing interface...',
        'Almost ready...'
    ]);

    // Add a small delay for loading, then fetch languages
    setTimeout(() => {
        fetchLanguages();
    }, 1500);
    
    function showLoader(message, progressMessages = []) {
        // Clear all pending timeouts
        currentLoaderTimeouts.forEach(timeoutId => clearTimeout(timeoutId));
        currentLoaderTimeouts = [];
        
        // Use the first message from progressMessages if provided, otherwise use the message parameter
        const displayMessage = progressMessages.length > 0 ? progressMessages[0] : message;
        
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
                        <div class="loader-text" id="loader-text">${displayMessage}</div>
                    </div>
                </div>
            </div>
        `;

        // Return function to stop loader
        return (immediate = false) => {
            // Clear all pending timeouts
            currentLoaderTimeouts.forEach(timeoutId => clearTimeout(timeoutId));
            currentLoaderTimeouts = [];
            
            // Remove loader HTML
            const loaderContainer = document.querySelector('.loader-container');
            if (loaderContainer) {
                if (immediate) {
                    // Remove immediately without fade animation
                    loaderContainer.remove();
                } else {
                    // Fade out animation
                    loaderContainer.style.opacity = '0';
                    const fadeTimeout = setTimeout(() => {
                        if (loaderContainer.parentNode) {
                            loaderContainer.remove();
                        }
                    }, 300);
                    currentLoaderTimeouts.push(fadeTimeout);
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
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        // Change messages periodically if multiple messages provided
        const loaderText = document.getElementById('submit-loader-text');
        let progressInterval = null;
        
        if (messages.length > 1) {
            progressInterval = setInterval(() => {
                currentMessageIndex = (currentMessageIndex + 1) % messages.length;
                if (loaderText) {
                    loaderText.style.opacity = '0';
                    setTimeout(() => {
                        if (loaderText) {
                            loaderText.textContent = messages[currentMessageIndex];
                            loaderText.style.opacity = '1';
                        }
                    }, 200);
                }
            }, 3000); // Change message every 3 seconds
        }

        // Return function to stop loader
        return () => {
            if (progressInterval) {
                clearInterval(progressInterval);
            }
            overlay.style.opacity = '0';
            setTimeout(() => overlay.remove(), 300);
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
                    // Don't stop loader yet - keep it running until form is rendered
                    renderQualityFeedbackForm(r.message, docname, stopLoaderCallback);
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

    function translateAllContent(data) {
        return new Promise((resolve) => {
            
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
        try {
            // Stop the animated loader (clear intervals) but keep a simple static loader visible
            // This prevents infinite loop while avoiding blank screen
            if (stopLoaderCallback) {
                stopLoaderCallback(true);
            }
            
            // Show static loader with same style as animated loader to prevent blank screen during translation
            const staticMessage = selectedLanguage !== 'en' ? 'Translating and preparing form...' : 'Preparing form...';
            showLoader(staticMessage);
            
            const employeeName = data.employee_name || '';
            const itemType = data.item_type || '';
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
                    'Employee ID:', 'Employee Name:', 'Operation Site:', 'Issued On:', 'Current Feedback Schedule:',
                    'Quality Feedback Questions', 'Survey Question', 'Rating Option:', 'Select Rating',
                    'Additional Details', 'Noticed Damage?:', 'No', 'Yes', 'Damage Description:',
                    'Describe any damage noticed...', 'Damage Attachment:', 'Attach', 'Feedback:',
                    'Share your feedback...', 'Submit Feedback', 'Submitting...',
                    'Very Poor', 'Poor', 'Average', 'Good', 'Excellent'
                ];
                questions = data.questions || [];
            } else {
                const translated = await translateAllContent(data);
                translations = translated.translations;
                questions = translated.questions;
            }

            const [
                helloText, tellAboutText, detailsTitle, employeeIdLabel, employeeNameLabel, operationSiteLabel,
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
                            <div class="detail-label">${employeeNameLabel}</div>
                            <div class="detail-value auto-fill">${employeeName}</div>
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
                                    <select class="form-control rating-select" name="question_${index + 1}_rating" data-parameter-name="${question.name || ''}">
                                        <option value="">${selectRatingText}</option>
                                        ${generateRatingOptions(question.options || [])}
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

            // Initialize form interactions immediately
            initializeFormInteractions(docname);
            
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
        } catch (error) {
            // Show error message if something goes wrong
            container.innerHTML = `
                <div class="alert alert-danger" style="margin: 20px; padding: 20px;">
                    <h4>Error Loading Form</h4>
                    <p>An error occurred while preparing the form. Please try again.</p>
                    <button class="btn btn-primary" onclick="location.reload()">Reload Page</button>
                </div>
            `;
        }
    }

    function generateRatingOptions(optionsArray) {
        if (!optionsArray || !Array.isArray(optionsArray) || optionsArray.length === 0) {
            return '';
        }
        
        // Generate options from the options array
        // Each option has 'option' (text) and 'score' (value) properties
        return optionsArray.map(opt => {
            const optionText = opt.option || '';
            const optionValue = opt.score !== undefined ? opt.score : opt.option;
            return `<option value="${optionValue}">${optionText}</option>`;
        }).join('');
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

        // Collect ratings with option text and score
        document.querySelectorAll('.rating-select').forEach((select) => {
            const selectedScore = select.value;
            const selectedOption = select.options[select.selectedIndex];
            const optionText = selectedOption ? selectedOption.text : '';
            const parameterName = select.getAttribute('data-parameter-name') || '';
            
            formData.ratings.push({
                parameter_name: parameterName,
                rating: selectedScore,
                rating_option: optionText,
                rating_score: selectedScore ? parseInt(selectedScore) : null
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
