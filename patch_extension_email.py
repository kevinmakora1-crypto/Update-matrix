import frappe

file_path = "one_fm/one_fm/doctype/employee_resignation_date_adjustment/employee_resignation_date_adjustment.py"

with open(file_path, "r") as f:
    content = f.read()

# Add the email logic directly after setting the deployment date
target_line = 'pmr.db_set("deployment_date", revised_deployment_date)'
new_code = '''pmr.db_set("deployment_date", revised_deployment_date)
                        
                        # Notify the recruiter about the date change
                        if getattr(pmr, "recruiter", None):
                            from one_fm.processor import sendemail
                            sendemail(
                                recipients=[pmr.recruiter],
                                subject=_("Action Required: Deployment Date Adjusted for PR {0}").format(pmr.name),
                                message=_("An employee involved in PR <b>{0}</b> has had their resignation date adjusted. The new deployment date for the replacement has been automatically updated to <b>{1}</b>. Please adjust your hiring schedules accordingly.").format(pmr.name, revised_deployment_date),
                                reference_doctype="Project Manpower Request",
                                reference_name=pmr.name
                            )'''

if "Notify the recruiter about the date change" not in content:
    content = content.replace(target_line, new_code)
    with open(file_path, "w") as f:
        f.write(content)
    print("Extension email logic added!")
else:
    print("Logic already exists.")

