from one_fm.custom.workflow.workflow import (
	delete_workflow, get_workflow_json_file, create_workflow
)
import logging


def execute():
    workflow_file = get_workflow_json_file("contracts.json")
    try:
        delete_workflow(workflow_file)
        create_workflow(workflow_file)
    except Exception:
        logging.exception(
            "Failed to update contracts workflow using file: %s",
            workflow_file,
        )
        raise