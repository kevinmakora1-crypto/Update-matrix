
// ── Inject horizontal connections CSS ──────────────────────────────
// Proven via browser test to flatten the Process Documents badges
// in the form dashboard connections section across all doctypes.
(function() {
  var s = document.createElement('style');
  s.id = 'one-fm-horizontal-connections';
  s.textContent = [
    'body .form-links .form-documents .row > [class*="col-md"] {',
    '  flex: 0 0 100% !important;',
    '  max-width: 100% !important;',
    '  display: flex !important;',
    '  flex-wrap: wrap !important;',
    '  align-items: center !important;',
    '  column-gap: 8px !important;',
    '  row-gap: 6px !important;',
    '}',
    'body .form-links .form-documents .form-link-title {',
    '  width: 100% !important;',
    '  flex-basis: 100% !important;',
    '}',
    'body .form-links .document-link {',
    '  display: inline-flex !important;',
    '  flex: none !important;',
    '  width: auto !important;',
    '}'
  ].join('\n');
  document.head.appendChild(s);
})();

// dom ready
document.addEventListener("DOMContentLoaded", (event)=>{
  // Add knowledge base to help button
  setTimeout(()=>{
    improve_my_erp();
    if(!frappe.user_roles.includes("System Manager")) {
      show_change_log();
    }
  }, 5000)
  knowledgeBase();
  quotes_flash();

});

var show_change_log=function() {
  let change_log = frappe.boot.change_log;
  if (
    !Array.isArray(change_log) ||
    !change_log.length ||
    window.Cypress ||
    cint(frappe.boot.sysdefaults.disable_change_log_notification)
  ) {
    return;
  }

  // Iterate over changelog
  var change_log_dialog = frappe.msgprint({
    message: frappe.render_template("change_log", { change_log: change_log }),
    title: __("Updated To A New Version 🎉"),
    wide: true,
  });
  change_log_dialog.keep_open = true;
  change_log_dialog.custom_onhide = function () {
    frappe.call({
      method: "frappe.utils.change_log.update_last_known_versions",
    });
  };
};

let improve_my_erp = () => {
	let improveBTN = document.createElement('a');
	improveBTN.classList = "btn btn-default btn-xs improve-my-erp";
	improveBTN.textContent = "Improve";
  improveBTN.href = '/helpdesk/tickets/new'
	document.querySelector(".form-inline.fill-width.justify-content-end").prepend(improveBTN);
}

// KNOWLEDGE BASE
let knowledgeBase = () => {
  // Add knowledge base to help button
//   console.log('red')
//  let helpbtn = $('#toolbar-help')[0]
//  let faq = document.createElement('a');
//  faq.id="faq";
//  faq.className = "dropdown-item";
//  faq.href="/knowledge_base";
//  faq.innerText = "knowledge Base";
//  helpbtn.appendChild(faq);
}


let quotes_flash = () => {
  show_quotes()
  setTimeout(()=>{
    show_quotes()
    // repeat
    quotes_flash()
  }, 3600000);
}

const show_quotes = () => {
  frappe.call({
    method: "one_fm.api.v2.zenquotes.run_quotes", //dotted path to server method
    callback: function(r) {
        //show_alert with indicator
        let data = r.message.results
        if (data) {
          frappe.show_alert({
            message:__(`${data.quote}<hr>Author: ${data.author}`),
            indicator:'green'
          }, 20);
        }
    }
  });
}
