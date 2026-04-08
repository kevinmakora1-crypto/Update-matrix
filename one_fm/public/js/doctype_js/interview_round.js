function sync_matrix(frm) {
    let source_questions = (frm.doc.interview_question || [])
        .map(function(source) {
            return source.questions;
        })
        .filter(function(question) {
            return !!question;
        });
    let target_matrix = frm.doc.interview_matrix || [];
    // Reuse existing matrix rows by question so row identities and typed data are preserved
    let matrix_map = {};
    target_matrix.forEach(function(row) {
        if (row.question && !matrix_map[row.question]) {
            matrix_map[row.question] = row;
        }
    });
    // Skip updates if the matrix is already in sync and in the right order
    let current_questions = target_matrix
        .map(function(row) {
            return row.question;
        })
        .filter(function(question) {
            return !!question;
        });
    let is_same_length = current_questions.length === source_questions.length;
    let is_same_order = is_same_length && source_questions.every(function(question, index) {
        return current_questions[index] === question;
    });
    if (is_same_order) {
        frm.refresh_field("interview_matrix");
        return;
    }
    // Remove only rows that no longer exist in the source question list
    target_matrix
        .filter(function(row) {
            return row.question && source_questions.indexOf(row.question) === -1;
        })
        .forEach(function(row) {
            frappe.model.clear_doc(row.doctype, row.name);
        });
    // Build the matrix in source order, reusing existing rows where possible
    let next_matrix = source_questions.map(function(question) {
        let existing_row = matrix_map[question];
        if (existing_row) {
            return existing_row;
        }
        let new_row = frm.add_child("interview_matrix");
        new_row.question = question;
        return new_row;
    });
    frm.doc.interview_matrix = next_matrix;
    frm.doc.interview_matrix.forEach(function(row, index) {
        row.idx = index + 1;
    });
    
    frm.refresh_field("interview_matrix");
}

frappe.ui.form.on('Interview Round', {
    refresh: function(frm) {
        frm.add_custom_button('Sync Matrix', () => sync_matrix(frm), 'Options');
    },
    validate: function(frm) {
        sync_matrix(frm);
    }
});

frappe.ui.form.on('Interview Questions', {
    questions: function(frm, cdt, cdn) {
        sync_matrix(frm);
    }
});
