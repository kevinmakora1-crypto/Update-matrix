from one_fm.custom.workflow.workflow import (
	get_workflow_json_file, create_workflow, delete_workflow
)


def execute():
    create_workflow(get_workflow_json_file("on_the_job_training.json"))