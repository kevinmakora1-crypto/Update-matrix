frappe.ready(() => {
    const container = document.getElementById('quality-feedback-container');
    const docname = frappe.boot.docname;

    if (!docname) {
        container.innerHTML = `<div class="alert alert-danger">Error: Quality Feedback document not specified.</div>`;
        return;
    }

    container.innerHTML = `
        <div class="container my-5">
            <div class="card">
                <div class="card-header"><h2>Quality Feedback</h2></div>
                <div class="card-body">
                    <form id="feedback-form">
                        <input type="hidden" id="feedback-docname" value="${docname}">
                        <div class="form-group">
                            <label for="feedback-field">Your Feedback:</label>
                            <textarea id="feedback-field" class="form-control" name="feedback_field" rows="4" required></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary mt-3">Submit</button>
                    </form>
                    <div id="feedback-response" class="mt-3"></div>
                </div>
            </div>
        </div>
    `;

    const form = document.getElementById('feedback-form');
    form.addEventListener('submit', (event) => {
        event.preventDefault();

        const feedbackValue = document.getElementById('feedback-field').value;
        const responseDiv = document.getElementById('feedback-response');
        
        form.querySelector('button[type="submit"]').disabled = true;

        frappe.call({
            method: 'one_fm.templates.pages.quality_feedback.submit_feedback',
            args: { docname, feedback: feedbackValue },
            callback: (r) => {
                if (r.message === 'success') {
                    responseDiv.innerHTML = `<div class="alert alert-success">Thank you! Your feedback has been submitted successfully.</div>`;
                    form.reset();
                } else {
                    responseDiv.innerHTML = `<div class="alert alert-danger">An error occurred while submitting your feedback. Please try again.</div>`;
                    form.querySelector('button[type="submit"]').disabled = false;
                }
            },
            error: () => {
                 responseDiv.innerHTML = `<div class="alert alert-danger">A server error occurred. Please try again later.</div>`;
                form.querySelector('button[type="submit"]').disabled = false;
            }
        });
    });
});
