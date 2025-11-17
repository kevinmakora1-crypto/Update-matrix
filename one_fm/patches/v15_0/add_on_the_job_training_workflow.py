from one_fm.custom.workflow.workflow import (
	delete_workflow, get_workflow_json_file, create_workflow
)


def execute():
    delete_workflow(get_workflow_json_file("on_the_job_training.json"))
    create_workflow(get_workflow_json_file("on_the_job_training.json"))