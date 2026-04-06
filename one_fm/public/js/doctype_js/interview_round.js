function sync_matrix(frm) {
    let source_questions = frm.doc.interview_question || [];
    let target_matrix = frm.doc.interview_matrix || [];
    
    // Create a map of existing matrix rows by question so we don't lose typed data
    let matrix_map = {};
    target_matrix.forEach(function(row) {
        if (row.question) {
            matrix_map[row.question] = row;
        }
    });
    
    // Clear and rebuild the matrix to stay 1-to-1 horizontally synced
    frm.clear_table("interview_matrix");
    
    source_questions.forEach(function(source) {
        if (!source.questions) return;
        
        let new_row = frm.add_child("interview_matrix");
        new_row.question = source.questions;
        
        // Restore old typed scores if they existed for this exact question
        if (matrix_map[source.questions]) {
            new_row.score_5 = matrix_map[source.questions].score_5;
            new_row.score_4 = matrix_map[source.questions].score_4;
            new_row.score_3 = matrix_map[source.questions].score_3;
            new_row.score_2 = matrix_map[source.questions].score_2;
            new_row.score_1 = matrix_map[source.questions].score_1;
        }
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
