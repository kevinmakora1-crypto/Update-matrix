frappe.ui.form.on("HD Ticket", {
  refresh: function (frm) {
    add_dev_ticket_button(frm);
    add_github_issue_button(frm);
  },
});

const add_github_issue_button = (frm) => {
  if (frm.doc.ticket_type == "Bug") {
    if (frm.doc.custom_github_issue_url) {
      if (!document.querySelector("#github_issue_span")) {
        let el = `<span id="github_issue_span">GitHub Issue has been created</span><br>
        <a href="${frm.doc.custom_github_issue_url}" class="btn btn-primary" target="_blank">View GitHub Issue</a>`;
        frm.dashboard.add_section(el, __("GitHub Issue"));
      }
    } else if (["Open", "Replied"].includes(frm.doc.status) && frappe.session.user==frm.doc.custom_bug_buster) {
      frm.add_custom_button(
        "GitHub Issue",
        () => {
          frappe.confirm(
            "Are you sure you want to create a GitHub issue?",
            () => {
              frappe.call({
                method: "one_fm.overrides.hd_ticket.create_github_issue",
                freeze: true,
                freeze_message: "Creating GitHub Issue",
                args: { name: frm.doc.name, description: frm.doc.description },
                callback: function (r) {
                  if (r.message.status == "success") {
                    frappe.msgprint("GitHub issue created successfully");
                    frm.refresh();
                    frm.reload_doc();
                  }
                },
              });
            },
            () => null
          );
        },
        "Create"
      );
    }
  }
};

const add_dev_ticket_button = (frm) => {
  if (
    frappe.user.has_role("System Manager") ||
    frappe.user.has_role("Issue User")
  ) {
    if (frm.doc.custom_dev_ticket) {
      // If Dev Ticket is already created
      if (!document.querySelector("#dev_ticket_span")) {
        let el = `<span id="dev_ticket_span">Dev Ticket has been created</span><br>
        <a href="${frm.doc.custom_dev_ticket}" class="btn btn-primary" target="_blank">View Dev Ticket</a>`;
        frm.dashboard.add_section(el, __("Dev Ticket"),);
      }
    } else if (["Open", "Replied"].includes(frm.doc.status)) {
      frm.add_custom_button(
        "Dev Ticket",
        () => {
          frappe.confirm(
            "Are you sure you create Dev Ticket?",
            () => {
              frappe.call({
                method: "one_fm.overrides.hd_ticket.create_dev_ticket",
                freeze: true,
                freeze_message: "Creating Dev Ticket",
                args: { name: frm.doc.name, description: frm.doc.description },
                callback: function (r) {
                  if (r.message.status == "success") {
                    frappe.msgprint(
                      "Dev ticket created successfully"
                    );
                    frm.refresh();
                    frm.reload_doc();
                  }
                },
              });
            },
            () => null
          );
        },
        "Create"
      );
    }
  }
};
