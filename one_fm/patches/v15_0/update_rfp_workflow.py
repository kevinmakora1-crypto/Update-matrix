from one_fm.custom.workflow.workflow import get_workflow_json_file, create_workflow, delete_workflow

def execute():
    delete_workflow(get_workflow_json_file("rfp.json"))
    create_workflow(get_workflow_json_file("rfp.json"))